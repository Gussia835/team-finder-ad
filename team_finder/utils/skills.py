from http import HTTPStatus

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from team_finder.constants import (
    JSON_KEY_ADDED,
    JSON_KEY_CREATED,
    JSON_KEY_ERROR,
    JSON_KEY_NAME,
    JSON_KEY_SKILL_ID,
    MAX_SKILLS_AUTOCOMPLETE,
    QueryParam,
)
from team_finder.utils.http import json_bad_request


def skills_autocomplete_payload(skill_model, query):
    skills = (
        skill_model.objects.filter(name__istartswith=query)
        .order_by('name')[:MAX_SKILLS_AUTOCOMPLETE]
    )
    return [{'id': skill.id, 'name': skill.name} for skill in skills]


def assign_skill(skill_model, skill_relation, body):
    skill_id = body.get(JSON_KEY_SKILL_ID)
    name = (body.get(JSON_KEY_NAME) or '').strip()

    if skill_id:
        skill = get_object_or_404(skill_model, pk=skill_id)
        created = False
    elif name:
        skill, created = skill_model.objects.get_or_create(name=name)
    else:
        return None, json_bad_request('skill_id or name required')

    added = False
    if not skill_relation.filter(pk=skill.pk).exists():
        skill_relation.add(skill)
        added = True

    status = HTTPStatus.CREATED if created else HTTPStatus.OK
    response = JsonResponse(
        {
            JSON_KEY_SKILL_ID: skill.id,
            JSON_KEY_NAME: skill.name,
            JSON_KEY_CREATED: created,
            JSON_KEY_ADDED: added,
        },
        status=status,
    )
    return skill, response


def autocomplete_query(request):
    return request.GET.get(QueryParam.Q, '')
