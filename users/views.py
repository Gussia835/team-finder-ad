from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from team_finder.constants import QueryParam
from team_finder.utils.http import parse_json_body
from team_finder.utils.mixins import QueryPrefixContextMixin
from team_finder.utils.skills import autocomplete_query
from users.constants import (
    MESSAGE_LOGIN_SUCCESS,
    MESSAGE_LOGOUT,
    MESSAGE_PASSWORD_CHANGED,
    MESSAGE_PROFILE_UPDATED,
    MESSAGE_REGISTER_SUCCESS,
    TEMPLATE_CHANGE_PASSWORD,
    TEMPLATE_EDIT_PROFILE,
    TEMPLATE_LOGIN,
    TEMPLATE_PARTICIPANTS,
    TEMPLATE_REGISTER,
    TEMPLATE_USER_DETAILS,
    USERS_PER_PAGE,
)
from users.forms import (
    LoginForm,
    ProfileEditForm,
    RegisterForm,
    UserPasswordChangeForm,
)
from users.models import User, UserSkill
from users.services import (
    add_user_skill,
    filter_participants_queryset,
    remove_user_skill,
    user_skills_autocomplete,
)
class UserListView(QueryPrefixContextMixin, ListView):
    model = User
    template_name = TEMPLATE_PARTICIPANTS
    context_object_name = 'participants'
    paginate_by = USERS_PER_PAGE

    def get_queryset(self):
        queryset = User.objects.all().prefetch_related('skills')
        return filter_participants_queryset(queryset, self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = UserSkill.objects.all().order_by('name')
        context['active_skill'] = self.request.GET.get(QueryParam.SKILL)
        context['active_filter'] = self.request.GET.get(QueryParam.FILTER)
        return context


class UserDetailView(DetailView):
    model = User
    template_name = TEMPLATE_USER_DETAILS
    context_object_name = 'user'

    def get_queryset(self):
        return User.objects.prefetch_related('owned_projects', 'skills')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.object == self.request.user
        return context


def register_view(request):
    if request.user.is_authenticated:
        return redirect('projects:list')

    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, MESSAGE_REGISTER_SUCCESS)
        return redirect('users:login')

    return render(request, TEMPLATE_REGISTER, {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:list')

    form = LoginForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        messages.success(request, MESSAGE_LOGIN_SUCCESS)
        return redirect('projects:list')

    return render(request, TEMPLATE_LOGIN, {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, MESSAGE_LOGOUT)
    return redirect('projects:list')


@login_required
def edit_profile_view(request):
    user = request.user
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
    )
    if form.is_valid():
        form.save()
        messages.success(request, MESSAGE_PROFILE_UPDATED)
        return redirect('users:user_detail', pk=user.pk)

    return render(
        request,
        TEMPLATE_EDIT_PROFILE,
        {'form': form, 'user': user},
    )


@login_required
def change_password_view(request):
    user = request.user
    form = UserPasswordChangeForm(user, request.POST or None)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, user)
        messages.success(request, MESSAGE_PASSWORD_CHANGED)
        return redirect('users:user_detail', pk=user.pk)

    return render(request, TEMPLATE_CHANGE_PASSWORD, {'form': form})


def skills_autocomplete(request):
    data = user_skills_autocomplete(autocomplete_query(request))
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_user_skill_view(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    return add_user_skill(
        profile_user,
        request.user,
        parse_json_body(request),
    )


@login_required
@require_POST
def remove_user_skill_view(request, pk, skill_id):
    profile_user = get_object_or_404(User, pk=pk)
    skill = get_object_or_404(UserSkill, pk=skill_id)
    return remove_user_skill(profile_user, request.user, skill)
