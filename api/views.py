from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import ProjectSerializer, UserSerializer
from projects.models import ProjectSkill
from projects.services import open_projects_queryset
from team_finder.constants import (
    JSON_KEY_FAVORITED,
    JSON_KEY_STATUS,
    JSON_STATUS_OK,
)
from team_finder.utils.mixins import SkillManagementMixin
from users.models import User, UserSkill


class ProjectViewSet(SkillManagementMixin, viewsets.ModelViewSet):
    skill_model = ProjectSkill
    skill_owner_field = 'owner'
    queryset = open_projects_queryset()
    serializer_class = ProjectSerializer
    ordering_fields = ['created_at', 'name']
    search_fields = ['name', 'description']
    filterset_fields = ['status']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def toggleFavorite(self, request, pk):
        user = request.user
        project = self.get_object()

        if (favorited := user.favorites.filter(pk=project.pk).exists()):
            user.favorites.remove(project)
        else:
            user.favorites.add(project)

        return Response({
            JSON_KEY_STATUS: JSON_STATUS_OK,
            JSON_KEY_FAVORITED: favorited,
        })


class UserViewSet(
    SkillManagementMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    skill_model = UserSkill
    queryset = User.objects.all().prefetch_related('skills', 'owned_projects')
    serializer_class = UserSerializer
    ordering_fields = ['surname', 'name', 'email', 'created_at']

    def get_owner_instance(self, instance):
        return instance
