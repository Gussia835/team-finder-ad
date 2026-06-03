from django.test import Client, TestCase
from django.urls import reverse
from projects.models import Project
from users.models import User, UserSkill


class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test',
            surname='User',
            password='testpass123',
        )

    def test_register_redirects_to_login(self):
        response = self.client.post(
            reverse('users:register'),
            {
                'email': 'new@example.com',
                'name': 'New',
                'surname': 'User',
                'password1': 'complexpass123',
                'password2': 'complexpass123',
            },
        )
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_login_success(self):
        response = self.client.post(
            reverse('users:login'),
            {'username': 'test@example.com', 'password': 'testpass123'},
        )
        self.assertRedirects(response, reverse('projects:list'))

    def test_logout_redirects_to_projects_list(self):
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(reverse('users:logout'))
        self.assertRedirects(response, reverse('projects:list'))


class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='owner@example.com',
            name='Owner',
            surname='One',
            password='testpass123',
        )

    def test_user_detail_page(self):
        response = self.client.get(
            reverse('users:user_detail', kwargs={'pk': self.user.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Owner One')

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse('users:edit_profile'))
        self.assertEqual(response.status_code, 302)

    def test_add_user_skill(self):
        self.client.login(username='owner@example.com', password='testpass123')
        response = self.client.post(
            reverse('users:add_skill', kwargs={'pk': self.user.pk}),
            data='{"name": "Go"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.user.skills.filter(name='Go').exists())

    def test_skills_autocomplete(self):
        UserSkill.objects.create(name='Python')
        response = self.client.get(
            reverse('users:skills_autocomplete'),
            {'q': 'Py'},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Python')


class UserListFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='u1@example.com',
            name='U1',
            surname='One',
            password='testpass123',
        )
        skill = UserSkill.objects.create(name='Rust')
        self.user.skills.add(skill)

    def test_filter_by_skill(self):
        response = self.client.get(
            reverse('users:user_list'),
            {'skill': 'Rust'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'U1 One')
