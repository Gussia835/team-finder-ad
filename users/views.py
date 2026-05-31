from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
from django.contrib import messages


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
