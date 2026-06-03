from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from api.serializers import (AddSkillSerializer,
                             UserSkillSerializer,
                             ProjectSkillSerializer)


class SkillManagementMixin:
    skill_model = None

    @action(detail=False,
            methods=['get'],
            url_path='skills',
            permission_classes=[IsAuthenticated])
    def skills_autocomplete(self, request):
        q = request.query_params.get('q', '')
        skills = self.skill_model.objects.filter(
                name__istartswith=q).order_by('name')[:10]

        if self.skill_model.__name__ == 'UserSkill':
            serializer = UserSkillSerializer(skills, many=True)
        else:
            serializer = ProjectSkillSerializer(skills, many=True)
        return Response(serializer.data)

    @action(detail=True,
            methods=['post'],
            url_path='skills/add',
            permission_classes=[IsAuthenticated])
    def add_skill(self, request, pk=None):
        instance = self.get_object()
        if not hasattr(instance, 'owner') or instance.owner != request.user:
            return Response({'error': 'Forbidden'},
                            status=status.HTTP_403_FORBIDDEN)

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
        if not getattr(instance, 'skills').filter(pk=skill.pk).exists():
            getattr(instance, 'skills').add(skill)
            added = True

        return Response({
            'skill_id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True,
            methods=['post'],
            url_path=r'skills/(?P<skill_id>[^/.]+)/remove',
            permission_classes=[IsAuthenticated])
    def remove_skill(self, request, pk=None, skill_id=None):
        instance = self.get_object()
        if not hasattr(instance, 'owner') or instance.owner != request.user:
            return Response({'error': 'Forbidden'},
                            status=status.HTTP_403_FORBIDDEN)

        skill = get_object_or_404(self.skill_model, pk=skill_id)
        getattr(instance, 'skills').remove(skill)
        return Response({'status': 'ok'})
