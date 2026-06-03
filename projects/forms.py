from django import forms

from team_finder.utils.mixins import GithubUrlValidationMixin

from .models import Project


class ProjectForm(GithubUrlValidationMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название проекта',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание проекта',
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/...',
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
