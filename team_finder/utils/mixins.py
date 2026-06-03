from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    AddSkillSerializer,
    ProjectSkillSerializer,
    UserSkillSerializer,
)
from team_finder.constants import GITHUB_HOST, MAX_SKILLS_AUTOCOMPLETE
from team_finder.utils.pagination import build_query_prefix
from team_finder.utils.skills import skills_autocomplete_payload


class GithubUrlValidationMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and GITHUB_HOST not in url:
            raise forms.ValidationError('Ссылка должна вести на GitHub')
        return url


class QueryPrefixContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query_prefix'] = build_query_prefix(self.request)
        return context


class SkillManagementMixin:
    skill_model = None
    skill_owner_field = 'owner'

    def _skill_serializer(self, skills):
        if self.skill_model.__name__ == 'UserSkill':
            return UserSkillSerializer(skills, many=True)
        return ProjectSkillSerializer(skills, many=True)

    def _can_manage_skills(self, instance, request):
        if self.skill_owner_field == 'owner':
            return instance.owner == request.user
        return instance == request.user

    @action(
        detail=False,
        methods=['get'],
        url_path='skills',
        permission_classes=[IsAuthenticated],
    )
    def skills_autocomplete(self, request):
        query = request.query_params.get('q', '')
        skills = (
            self.skill_model.objects.filter(name__istartswith=query)
            .order_by('name')[:MAX_SKILLS_AUTOCOMPLETE]
        )
        return Response(self._skill_serializer(skills).data)

    @action(
        detail=True,
        methods=['post'],
        url_path='skills/add',
        permission_classes=[IsAuthenticated],
    )
    def add_skill(self, request, pk=None):
        instance = self.get_object()
        if not self._can_manage_skills(instance, request):
            return Response(
                {'error': 'Forbidden'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddSkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        skill_id = serializer.validated_data.get('skill_id')
        name = serializer.validated_data.get('name')

        if skill_id:
            skill = get_object_or_404(self.skill_model, pk=skill_id)
            created = False
        else:
            skill, created = self.skill_model.objects.get_or_create(name=name)

        added = False
        if not instance.skills.filter(pk=skill.pk).exists():
            instance.skills.add(skill)
            added = True

        return Response(
            {
                'skill_id': skill.id,
                'name': skill.name,
                'created': created,
                'added': added,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=['post'],
        url_path=r'skills/(?P<skill_id>[^/.]+)/remove',
        permission_classes=[IsAuthenticated],
    )
    def remove_skill(self, request, pk=None, skill_id=None):
        instance = self.get_object()
        if not self._can_manage_skills(instance, request):
            return Response(
                {'error': 'Forbidden'},
                status=status.HTTP_403_FORBIDDEN,
            )

        skill = get_object_or_404(self.skill_model, pk=skill_id)
        instance.skills.remove(skill)
        return Response({'status': 'ok'})
