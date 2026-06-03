import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

User = get_user_model()

PHONE_PATTERN = re.compile(r'^(8\d{10}|\+7\d{10})$')


def normalize_phone(phone):
    phone = phone.strip()
    if phone.startswith('8') and len(phone) == 11:
        return '+7' + phone[1:]
    return phone


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя',
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия',
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пароль',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Повторите пароль',
            }),
        }


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
        }),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
        }),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

    def get_invalid_login_error(self):
        return forms.ValidationError(
            'Неверный email или пароль',
            code='invalid_login',
        )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control',
                                           'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'id': 'id_avatar',
                                             'class': 'hidden'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return ''
        if not PHONE_PATTERN.match(phone):
            raise forms.ValidationError(
                'Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX',
            )
        phone = normalize_phone(phone)
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Этот номер телефона уже используется')
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and 'github.com' not in url:
            raise forms.ValidationError('Ссылка должна вести на GitHub')
        return url


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
