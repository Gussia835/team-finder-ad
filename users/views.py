from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from .models import User
from django.views.generic import ListView, DetailView
from .models import UserSkill
from django.db.models import Q


print('users.views')

class UserListView(ListView):
    '''cтраница списка всех'''
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    paginate_by = 12
    ordering = ['id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # вариант 2

        context['all_skills'] = UserSkill.objects.all().order_by('name')
        context['active_skill'] = self.request.GET.get('skill')
        # вариант 1
        context['active_filter'] = self.request.GET.get('filter')
        return context

    def get_queryset(self):
        queryset = User.objects.all().prefetch_related('skills')

        # вариант 2
        skill_name = self.request.GET.get('skill')
        if skill_name and self.request.user.is_authenticated:
            queryset = queryset.filter(skills__name__iexact=skill_name
                                       ).distinct()

        # вариант 1
        filter_type = self.request.GET.get('filter')
        if filter_type and self.request.user.is_authenticated:
            user = self.request.user
            if filter_type == 'favorites_authors':

                queryset = queryset.filter(
                    owned_projects__in=user.favorites.all()
                ).distinct()
            elif filter_type == 'my_projects_authors':

                queryset = queryset.filter(
                    owned_projects__in=user.participated_projects.all()
                ).distinct()

            elif filter_type == 'liked_my_projects':
                queryset = queryset.filter(
                    favorites__in=user.owned_projects.all()
                ).distinct()

            elif filter_type == 'my_projects_participants':
                queryset = queryset.filter(
                    participated_projects__in=user.owned_projects.all()
                ).distinct()

        return queryset


class UserDetailView(DetailView):
    '''cтраница профиля'''
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        request_user = self.request.user

        context['owned_projects'] = user.owned_projects.filter(
            Q(status='open') | Q(status='Open')
        ).select_related('owner')

        context['is_owner'] = user == request_user

        return context


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, 'Регистрация успешна!')
            return redirect('projects:list')

    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    '''Вход'''

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(request, 'Добро пожаловать!')
            return redirect('projects:list')

    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    '''Выход из аккаунта'''

    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('users:login')
