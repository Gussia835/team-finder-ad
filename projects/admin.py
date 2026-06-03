from django.contrib import admin

from .models import Project, ProjectSkill


@admin.register(ProjectSkill)
class ProjectSkillAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    filter_horizontal = ('participants', 'skills')
    raw_id_fields = ('owner',)
