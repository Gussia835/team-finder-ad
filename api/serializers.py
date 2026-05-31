from rest_framework import serializers
from users.models import User, UserSkill
from projects.models import Project, ProjectSkill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSkill
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

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
