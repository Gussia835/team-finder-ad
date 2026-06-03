from django.http import JsonResponse

from team_finder.constants import JSON_KEY_STATUS, JSON_STATUS_OK, QueryParam
from team_finder.utils.http import json_forbidden
from team_finder.utils.skills import assign_skill, skills_autocomplete_payload
from users.constants import UserFilterType
from users.models import User, UserSkill


def filter_participants_queryset(queryset, request):
    skill_name = request.GET.get(QueryParam.SKILL)
    if skill_name:
        queryset = queryset.filter(
            skills__name__iexact=skill_name,
        ).distinct()

    filter_type = request.GET.get(QueryParam.FILTER)
    if not filter_type or not request.user.is_authenticated:
        return queryset

    user = request.user
    filters = {
        UserFilterType.OWNERS_OF_FAVORITE_PROJECTS: lambda: queryset.filter(
            owned_projects__in=user.favorites.all(),
        ).distinct(),
        UserFilterType.OWNERS_OF_PARTICIPATING_PROJECTS: lambda: queryset.filter(
            owned_projects__in=user.participated_projects.all(),
        ).distinct(),
        UserFilterType.INTERESTED_IN_MY_PROJECTS: lambda: queryset.filter(
            favorites__in=user.owned_projects.all(),
        ).distinct(),
        UserFilterType.PARTICIPANTS_OF_MY_PROJECTS: lambda: queryset.filter(
            participated_projects__in=user.owned_projects.all(),
        ).distinct(),
    }
    handler = filters.get(filter_type)
    if handler:
        return handler()
    return queryset


def user_skills_autocomplete(query):
    return skills_autocomplete_payload(UserSkill, query)


def add_user_skill(profile_user, request_user, body):
    if profile_user != request_user:
        return json_forbidden()
    _, response = assign_skill(UserSkill, profile_user.skills, body)
    return response


def remove_user_skill(profile_user, request_user, skill):
    if profile_user != request_user:
        return json_forbidden()
    profile_user.skills.remove(skill)
    return JsonResponse({JSON_KEY_STATUS: JSON_STATUS_OK})
