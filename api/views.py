from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    ProjectSerializer,
    UserSerializer,
)
from projects.models import Project, ProjectSkill
from users.models import User, UserSkill
from team_finder.utils.mixins import SkillManagementMixin


class ProjectViewSet(SkillManagementMixin, viewsets.ModelViewSet):
    skill_model = ProjectSkill
    queryset = Project.objects.filter(
        Q(status='open') | Q(status='Open')
    ).select_related('owner').prefetch_related('participants', 'skills')

    serializer_class = ProjectSerializer
    ordering_fields = ['created_at', 'name']
    search_fields = ['name', 'description']
    filterset_fields = ['status']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, pk):
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


class UserViewSet(SkillManagementMixin, mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    skill_model = UserSkill
    queryset = User.objects.all().select_related(
    ).prefetch_related('skills', 'owned_projects')
    serializer_class = UserSerializer
    ordering_fields = ['id', 'created_at']
