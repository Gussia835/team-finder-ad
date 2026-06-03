from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, UserSkill


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('email', 'name', 'surname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'name', 'surname')
    ordering = ('email',)
    filter_horizontal = ('skills', 'favorites', 'groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Профиль', {
            'fields': (
                'name', 'surname', 'avatar', 'phone',
                'github_url', 'about', 'skills', 'favorites',
            ),
        }),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'password1', 'password2',
            ),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
