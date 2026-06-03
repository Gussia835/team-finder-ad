from django.test import TestCase
from projects.models import Project
from rest_framework.test import APIClient
from users.models import User


class ApiV1Tests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='api@example.com',
            name='Api',
            surname='User',
            password='testpass123',
        )
        self.project = Project.objects.create(
            name='API Project',
            owner=self.user,
            status='open',
        )

    def test_projects_list(self):
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, 200)

    def test_toggle_favorite_action(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/v1/projects/{self.project.pk}/toggleFavorite/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['favorited'])
