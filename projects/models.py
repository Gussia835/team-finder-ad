from django.conf import settings
from django.db import models

from team_finder.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_SKILL_NAME_MAX_LENGTH,
    PROJECT_STATUS_MAX_LENGTH,
    PROJECT_STATUSES,
    ProjectStatus,
)


class ProjectSkill(models.Model):
    name = models.CharField(
        max_length=PROJECT_SKILL_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык проекта'
        verbose_name_plural = 'Навыки проектов'

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(
        max_length=PROJECT_NAME_MAX_LENGTH,
        verbose_name='Название проекта',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание проекта',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор проекта',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на Github',
    )
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUSES,
        default=ProjectStatus.OPEN,
        verbose_name='Статус',
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники',
    )
    skills = models.ManyToManyField(
        ProjectSkill,
        related_name='projects',
        blank=True,
        verbose_name='Необходимые навыки',
    )

    def complete(self):
        self.status = ProjectStatus.CLOSED
        self.save()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name
