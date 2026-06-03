from django.db import models
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from PIL import Image, ImageDraw, ImageFont
import random
from django.core.files.base import ContentFile
import io


class CustomUserManager(BaseUserManager):
    def create_user(self,
                    email,
                    name,
                    surname,
                    password=None,
                    **extra):

        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email,
                          name=name,
                          surname=surname,
                          **extra)

        if password:
            user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email,
                         name,
                         surname,
                         password=None,
                         **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)

        return self.create_user(email, name, surname, password, **extra)


# Вариант 2
class UserSkill(models.Model):
    name = models.CharField(max_length=124,
                            unique=True,
                            verbose_name='Название навыка')

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True,
                              verbose_name='email')
    name = models.CharField(max_length=124,
                            verbose_name='Имя пользователя')
    surname = models.CharField(max_length=124,
                               verbose_name='Фамилия пользователя')
    avatar = models.ImageField(upload_to='avatars/',
                               blank=True,
                               null=True,
                               verbose_name='Аватарка пользователя')
    phone = models.CharField(max_length=12,
                             blank=True,
                             default='',
                             verbose_name='Номер телефона')
    github_url = models.URLField(blank=True,
                                 null=True,
                                 verbose_name='Ссылка на Github')
    about = models.TextField(max_length=256,
                             blank=True,
                             verbose_name='Описание профиля')
    is_active = models.BooleanField(default=True,
                                    verbose_name='Активный пользователь')
    is_staff = models.BooleanField(default=False,
                                   verbose_name='Администратор')
    # 2 вариант
    skills = models.ManyToManyField(UserSkill,
                                    related_name='users',
                                    blank=True,
                                    verbose_name='Навыки')
    # 1 вариант
    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True,
        verbose_name='Избранные проекты'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def _generate_default_avatar(self):
        '''Квадратная картинка с первой буквой имени на случайном фоне'''

        try:
            colors = ['#A8DADC',
                      '#457B9D',
                      '#E63946',
                      '#F1FAEE',
                      '#A8DADC',
                      '#8AB17D']

            bg_color = random.choice(colors)

            img = Image.new('RGB', (200, 200), color=bg_color)
            draw = ImageDraw.Draw(img)

            initial = self.name[0].upper() if self.name else 'U'

            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except IOError:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), initial, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            x = (200 - text_w) // 2
            y = (200 - text_h) // 2

            draw.text((x, y), initial, fill='white', font=font)

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            self.avatar.save(f'avatar_{self.email}.png',
                             ContentFile(buffer.read()), save=False)
        except Exception as e:
            print(f'Ошибка генерации аватара: {e}')

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self._generate_default_avatar()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname}'
