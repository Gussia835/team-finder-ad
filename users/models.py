import io
import logging
import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_COLORS,
    AVATAR_DEFAULT_INITIAL,
    AVATAR_FONT_SIZE,
    AVATAR_SIZE,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
)
from users.managers import UserManager

logger = logging.getLogger(__name__)


class UserSkill(models.Model):
    name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название навыка',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='email')
    name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        verbose_name='Имя пользователя',
    )
    surname = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        verbose_name='Фамилия пользователя',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватарка пользователя',
    )
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
        default='',
        verbose_name='Номер телефона',
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на Github',
    )
    about = models.TextField(
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
        verbose_name='Описание профиля',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный пользователь',
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Администратор',
    )
    skills = models.ManyToManyField(
        UserSkill,
        related_name='users',
        blank=True,
        verbose_name='Навыки',
    )
    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True,
        verbose_name='Избранные проекты',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def _generate_default_avatar(self):
        try:
            bg_color = random.choice(AVATAR_COLORS)
            img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color=bg_color)
            draw = ImageDraw.Draw(img)
            initial = (self.name[0].upper()
                       if self.name else AVATAR_DEFAULT_INITIAL)

            try:
                font = ImageFont.truetype('arial.ttf', AVATAR_FONT_SIZE)
            except OSError:
                try:
                    font = ImageFont.truetype('DejaVuSans.ttf',
                                              AVATAR_FONT_SIZE)
                except OSError:
                    logger.warning(
                        "Шрифты 'arial.ttf' и 'DejaVuSans.ttf' недоступны"
                    )
                    try:
                        font = ImageFont.load_default(size=AVATAR_FONT_SIZE)
                    except TypeError:
                        font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), initial, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            x = (AVATAR_SIZE - text_w) // 2
            y = (AVATAR_SIZE - text_h) // 2
            draw.text((x, y), initial, fill='white', font=font)

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            self.avatar.save(
                f'avatar_{self.email}.png',
                ContentFile(buffer.read()),
                save=False,
            )
        except Exception as exc:
            logger.warning('Ошибка генерации аватара: %s', exc)

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self._generate_default_avatar()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['surname', 'name', 'email']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname}'
