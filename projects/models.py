from django.db import models
from django.conf import settings


class ProjectSkill(models.Model):
    name = models.CharField(max_length=124,
                            unique=True,
                            verbose_name='Название')

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык проекта'
        verbose_name_plural = 'Навыки проектов'

    def __str__(self):
        return self.name


class Project(models.Model):
    AVAILABLE_STATUS = [('open', 'Open'),
                        ('closed', 'Closed')]

    name = models.CharField(max_length=200,
                            verbose_name='Название проекта')
    description = models.TextField(blank=True,
                                   verbose_name='Описание проекта')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='owner_projects',
                              verbose_name='Автор проекта')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания')
    github_url = models.URLField(blank=True,
                                 null=True,
                                 verbose_name='Ссылка на Github')

    status = models.CharField(max_length=6,
                              choices=AVAILABLE_STATUS,
                              default='open',
                              verbose_name='Статус')

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          related_name='participant_projects',
                                          blank=True,
                                          verbose_name='Участники')
    # 3 вариант
    skills = models.ManyToManyField(
        ProjectSkill,
        related_name='projects',
        blank=True,
        verbose_name='Необходимые навыки'
    )

    def complete(self):
        '''смена статуса проекта на closed'''

        self.status = 'closed'
        self.save()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name
