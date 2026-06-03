from http import HTTPStatus

from django.http import JsonResponse

from team_finder.constants import (
    JSON_KEY_FAVORITED,
    JSON_KEY_PARTICIPANT,
    JSON_KEY_PROJECT_STATUS,
    JSON_KEY_STATUS,
    JSON_STATUS_OK,
    ProjectStatus,
)
from team_finder.utils.http import json_forbidden
from team_finder.utils.skills import assign_skill, skills_autocomplete_payload
from projects.models import Project, ProjectSkill


def open_projects_queryset():
    return (
        Project.objects.filter(status=ProjectStatus.OPEN)
        .select_related('owner')
        .prefetch_related('skills', 'participants')
    )


def filter_projects_by_skill(queryset, skill_name):
    if not skill_name:
        return queryset
    return queryset.filter(skills__name__iexact=skill_name).distinct()


def project_skills_autocomplete(query):
    return skills_autocomplete_payload(ProjectSkill, query)


def toggle_favorite(user, project):
    favorited = False
    if user.favorites.filter(pk=project.pk).exists():
        user.favorites.remove(project)
    else:
        user.favorites.add(project)
        favorited = True
    return JsonResponse({JSON_KEY_STATUS: JSON_STATUS_OK, JSON_KEY_FAVORITED: favorited})


def complete_project(project, user):
    if project.owner_id != user.pk or project.status != ProjectStatus.OPEN:
        return json_forbidden()
    project.complete()
    return JsonResponse({
        JSON_KEY_STATUS: JSON_STATUS_OK,
        JSON_KEY_PROJECT_STATUS: ProjectStatus.CLOSED,
    })


def toggle_participation(project, user):
    if project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
        return JsonResponse({
            JSON_KEY_STATUS: JSON_STATUS_OK,
            JSON_KEY_PARTICIPANT: False,
        })
    project.participants.add(user)
    return JsonResponse({
        JSON_KEY_STATUS: JSON_STATUS_OK,
        JSON_KEY_PARTICIPANT: True,
    })


def add_project_skill(project, user, body):
    if project.owner_id != user.pk:
        return json_forbidden()
    _, response = assign_skill(ProjectSkill, project.skills, body)
    return response


def remove_project_skill(project, user, skill):
    if project.owner_id != user.pk:
        return json_forbidden()
    project.skills.remove(skill)
    return JsonResponse({JSON_KEY_STATUS: JSON_STATUS_OK})
