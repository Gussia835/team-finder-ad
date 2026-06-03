from rest_framework import serializers

from users.models import User, UserSkill
from projects.models import Project, ProjectSkill
from team_finder.constants import PROJECT_SKILL_NAME_MAX_LENGTH


class UserSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSkill
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    skills = UserSkillSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id',
                  'email',
                  'name',
                  'surname',
                  'avatar',
                  'phone',
                  'github_url',
                  'about',
                  'skills']
        read_only_fields = ['id',
                            'email',
                            'skills']


class ProjectSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSkill
        fields = ['id', 'name']


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(read_only=True)
    participants = serializers.StringRelatedField(many=True, read_only=True)
    skills = ProjectSkillSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id',
                  'name',
                  'description',
                  'owner',
                  'participants',
                  'skills',
                  'created_at',
                  'github_url',
                  'status']
        read_only_fields = ['id',
                            'owner',
                            'participants',
                            'created_at']

    def get_owner(self, obj):
        return {'name': obj.owner.name, 'surname': obj.owner.surname}


class AddSkillSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False,
                                 max_length=PROJECT_SKILL_NAME_MAX_LENGTH)

    def validate(self, data):
        if not data.get('skill_id') and not data.get('name'):
            raise serializers.ValidationError('Укажите skill_id или name')
        return data
