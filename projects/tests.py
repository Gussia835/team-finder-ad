import json

from django.test import Client, TestCase
from django.urls import reverse
from projects.models import Project, ProjectSkill
from users.models import User


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            email='owner@example.com',
            name='Owner',
            surname='Test',
            password='testpass123',
        )
        self.other = User.objects.create_user(
            email='other@example.com',
            name='Other',
            surname='User',
            password='testpass123',
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Description',
            owner=self.owner,
            status='open',
        )
        self.project.participants.add(self.owner)

    def test_project_list_page(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_root_redirects_to_project_list(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/projects/list/')

    def test_create_project_url(self):
        self.client.login(username='owner@example.com', password='testpass123')
        response = self.client.get(reverse('projects:create'))
        self.assertEqual(response.status_code, 200)

    def test_toggle_favorite(self):
        self.client.login(username='other@example.com', password='testpass123')
        url = reverse('projects:toggle_favorite', kwargs={'pk': self.project.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['favorited'])
        self.assertEqual(self.other.favorites.count(), 1)

    def test_complete_project(self):
        self.client.login(username='owner@example.com', password='testpass123')
        url = reverse('projects:complete', kwargs={'pk': self.project.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'closed')

    def test_toggle_participate(self):
        self.client.login(username='other@example.com', password='testpass123')
        url = reverse(
            'projects:toggle_participate',
            kwargs={'pk': self.project.pk},
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['participant'])
        self.assertTrue(
            self.project.participants.filter(pk=self.other.pk).exists(),
        )

    def test_closed_project_not_on_list(self):
        self.project.status = 'closed'
        self.project.save()
        response = self.client.get(reverse('projects:list'))
        self.assertNotContains(response, 'Test Project')

    def test_add_project_skill(self):
        self.client.login(username='owner@example.com', password='testpass123')
        url = reverse('projects:add_skill', kwargs={'pk': self.project.pk})
        response = self.client.post(
            url,
            data=json.dumps({'name': 'Docker'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.project.skills.filter(name='Docker').exists())

    def test_filter_projects_by_skill(self):
        skill = ProjectSkill.objects.create(name='Vue')
        self.project.skills.add(skill)
        response = self.client.get(
            reverse('projects:list'),
            {'skill': 'Vue'},
        )
        self.assertContains(response, 'Test Project')
