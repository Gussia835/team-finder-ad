from django.shortcuts import get_object_or_404
from users.models import User, UserSkill
from projects.models import Project, ProjectSkill
from .serializers import (UserSerializer,
                          ProjectSerializer,
                          UserSkillSerializer,
                          ProjectSkillSerializer,
                          AddSkillSerializer)
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.filter(
        Q(status='open') | Q(status='Open')
    ).select_related('owner').prefetch_related('participants', 'skills')

    serializer_class = ProjectSerializer
    ordering_fields = ['created_at', 'name']
    search_fields = ['name', 'description']
    filterset_fields = ['status']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # 1 вариант
    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def toggleFavorite(self, request, pk):
        user = request.user
        project = self.get_object()
        favorited = False

        if user.favorites.filter(pk=project.pk).exists():
            user.favorites.remove(project)

        else:
            user.favorites.add(project)
            favorited = True

        return Response({'status': 'ok',
                         'favorited': favorited})

    # 3 вариант
    @action(detail=False,
            methods=['get'],
            url_path='skills',
            permission_classes=[IsAuthenticated])
    def skills_autocomplete(self, request):
        q = request.query_params.get('q', '')
        skills = ProjectSkill.objects.filter(name__istartswith=q).order_by('name')[:10]
        return Response(ProjectSkillSerializer(skills, many=True).data)

    # 3 вариант
    @action(detail=True, methods=['post'],
            url_path='skills/add',
            permission_classes=[IsAuthenticated])
    def add_skill(self, request, pk=None):
        project = self.get_object()
        if project.owner != request.user:
            return Response({'error': 'Forbidden'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = AddSkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        skill_id = serializer.validated_data.get('skill_id')
        name = serializer.validated_data.get('name')

        if skill_id:
            skill = get_object_or_404(ProjectSkill, pk=skill_id)
            created = False
        else:
            skill, created = ProjectSkill.objects.get_or_create(name=name)

        added = False
        if not project.skills.filter(pk=skill.pk).exists():
            project.skills.add(skill)
            added = True

        return Response({
            'skill_id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    # 3 вариант
    @action(detail=True,
            methods=['post'],
            url_path='skills/(?P<skill_id>[^/.]+)/remove',
            permission_classes=[IsAuthenticated])
    def remove_skill(self, request, pk=None, skill_id=None):
        project = self.get_object()
        skill = get_object_or_404(ProjectSkill, pk=skill_id)

        if project.owner != request.user:
            return Response({'error': 'Forbidden'},
                            status=status.HTTP_403_FORBIDDEN)

        project.skills.remove(skill)
        return Response({'status': 'ok'})


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    '''API для пользователей: список + детали + навыки'''
    queryset = User.objects.all().select_related(
    ).prefetch_related('skills', 'owned_projects')
    serializer_class = UserSerializer
    ordering_fields = ['id', 'created_at']

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def skills_autocomplete(self, request):
        q = request.query_params.get('q', '')
        skills = UserSkill.objects.filter(name__istartswith=q).order_by('name')[:10]
        return Response(UserSkillSerializer(skills, many=True).data)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def add_skill(self, request, pk=None):
        user = self.get_object()
        if user != request.user:
            return Response({'error': 'Forbidden'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = AddSkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        skill_id = serializer.validated_data.get('skill_id')
        name = serializer.validated_data.get('name')

        if skill_id:
            skill = get_object_or_404(UserSkill, pk=skill_id)
            created = False
        else:
            skill, created = UserSkill.objects.get_or_create(name=name)

        added = False
        if not user.skills.filter(pk=skill.pk).exists():
            user.skills.add(skill)
            added = True

        return Response({
            'skill_id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True,
            methods=['post'],
            url_path='skills/(?P<skill_id>[^/.]+)/remove',
            permission_classes=[IsAuthenticated])
    def remove_skill(self, request, pk=None, skill_id=None):
        user = self.get_object()
        skill = get_object_or_404(UserSkill, pk=skill_id)

        if user != request.user:
            return Response({'error': 'Forbidden'},
                            status=status.HTTP_403_FORBIDDEN)

        user.skills.remove(skill)
        return Response({'status': 'ok'})
