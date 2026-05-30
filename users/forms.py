from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    '''Форма регистрации'''
    class Meta:
        model = User
        fields = ('email',
                  'name', 'surname'
                  'password1', 'password2')
        widgets = {
            'email': forms.EmailField(attrs={
                                            'class': 'form-control',
                                            'placeholder': 'Email'
                                            }),
            'name': forms.TextInput(attrs={
                                            'class': 'form-control',
                                            'placeholder': 'Имя'
            }),
            'surname': forms.TextInput(attrs={
                                            'class': 'form-control',
                                            'placeholder': 'Фамилия'
            }),
            'password1': forms.PasswordInput(attrs={
                                            'class': 'form-control',
                                            'placeholder': 'Пароль'
            }),
            'password2': forms.PasswordInput(attrs={
                                            'class': 'form-control',
                                            'placeholder': 'Повторите пароль'
            }),
        }


class LoginForm(AuthenticationForm):
    '''Форма входа'''
    username = forms.EmailField(label='Email',
                                attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Email'
                                })
    password = forms.CharField(label='Пароль',
                               attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Пароль'
                               })
