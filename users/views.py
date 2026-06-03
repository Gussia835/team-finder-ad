import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .forms import (
    LoginForm,
    ProfileEditForm,
    RegisterForm,
    UserPasswordChangeForm,
)
from .models import User, UserSkill


class UserListView(ListView):
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    paginate_by = 12

    def get_queryset(self):
        queryset = User.objects.all().prefetch_related('skills')
        skill_name = self.request.GET.get('skill')
        if skill_name:
            queryset = queryset.filter(
                skills__name__iexact=skill_name,
            ).distinct()

        filter_type = self.request.GET.get('filter')
        if filter_type and self.request.user.is_authenticated:
            user = self.request.user
            if filter_type == 'owners-of-favorite-projects':
                queryset = queryset.filter(
                    owned_projects__in=user.favorites.all(),
                ).distinct()
            elif filter_type == 'owners-of-participating-projects':
                queryset = queryset.filter(
                    owned_projects__in=user.participated_projects.all(),
                ).distinct()
            elif filter_type == 'interested-in-my-projects':
                queryset = queryset.filter(
                    favorites__in=user.owned_projects.all(),
                ).distinct()
            elif filter_type == 'participants-of-my-projects':
                queryset = queryset.filter(
                    participated_projects__in=user.owned_projects.all(),
                ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = UserSkill.objects.all().order_by('name')
        context['active_skill'] = self.request.GET.get('skill')
        context['active_filter'] = self.request.GET.get('filter')
        params = self.request.GET.copy()
        params.pop('page', None)
        context['query_prefix'] = params.urlencode()
        if context['query_prefix']:
            context['query_prefix'] += '&'
        return context


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
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
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна! Войдите в аккаунт.')
            return redirect('users:login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:list')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Добро пожаловать!')
            return redirect('projects:list')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('projects:list')


@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('users:user_detail', pk=user.pk)
    else:
        form = ProfileEditForm(instance=user)
    return render(
        request,
        'users/edit_profile.html',
        {'form': form, 'user': user},
    )


@login_required
def change_password_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserPasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль изменён')
            return redirect('users:user_detail', pk=user.pk)
    else:
        form = UserPasswordChangeForm(user)
    return render(request, 'users/change_password.html', {'form': form})


def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = (
        UserSkill.objects.filter(name__istartswith=q)
        .order_by('name')[:10]
    )
    data = [{'id': s.id, 'name': s.name} for s in skills]
    return JsonResponse(data, safe=False)


def _json_body(request):
    if request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return {}
    return {}


@login_required
@require_POST
def add_user_skill(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    if profile_user != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    body = _json_body(request)
    skill_id = body.get('skill_id')
    name = (body.get('name') or '').strip()

    if skill_id:
        skill = get_object_or_404(UserSkill, pk=skill_id)
        created = False
    elif name:
        skill, created = UserSkill.objects.get_or_create(name=name)
    else:
        return JsonResponse({'error': 'skill_id or name required'}, status=400)

    added = False
    if not profile_user.skills.filter(pk=skill.pk).exists():
        profile_user.skills.add(skill)
        added = True

    status_code = 201 if created else 200
    return JsonResponse(
        {
            'skill_id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added,
        },
        status=status_code,
    )


@login_required
@require_POST
def remove_user_skill(request, pk, skill_id):
    profile_user = get_object_or_404(User, pk=pk)
    skill = get_object_or_404(UserSkill, pk=skill_id)
    if profile_user != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    profile_user.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
