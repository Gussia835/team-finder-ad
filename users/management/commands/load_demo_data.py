from django.core.management.base import BaseCommand
from projects.models import Project, ProjectSkill
from users.models import User, UserSkill

DEMO_PASSWORD = 'demo12345'


class Command(BaseCommand):
    help = 'Создаёт или обновляет демо-пользователей и проекты для ревью'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать демо-проекты',
        )

    def handle(self, *args, **options):
        alice, _ = User.objects.get_or_create(
            email='alice@example.com',
            defaults={
                'name': 'Алиса',
                'surname': 'Иванова',
                'phone': '+79001111111',
                'about': 'Full-stack разработчик',
                'github_url': 'https://github.com/alice',
            },
        )
        bob, _ = User.objects.get_or_create(
            email='bob@example.com',
            defaults={
                'name': 'Борис',
                'surname': 'Петров',
                'phone': '+79002222222',
                'about': 'Дизайнер интерфейсов',
                'github_url': 'https://github.com/bob',
            },
        )

        for user in (alice, bob):
            user.set_password(DEMO_PASSWORD)
            user.is_active = True
            user.save()

        python_skill, _ = UserSkill.objects.get_or_create(name='Python')
        django_skill, _ = UserSkill.objects.get_or_create(name='Django')
        react_skill, _ = UserSkill.objects.get_or_create(name='React')
        alice.skills.set([python_skill, django_skill])
        bob.skills.set([react_skill])

        if options['force']:
            Project.objects.filter(
                name__in=['TeamFinder Clone', 'Мобильный трекер привычек'],
            ).delete()

        if not Project.objects.filter(name='TeamFinder Clone').exists():
            proj_skill_py, _ = ProjectSkill.objects.get_or_create(
                                                    name='Python')
            proj_skill_dj, _ = ProjectSkill.objects.get_or_create(
                                                    name='Django')

            p1 = Project.objects.create(
                name='TeamFinder Clone',
                description='Платформа для поиска команды на pet-проекты',
                owner=alice,
                github_url='https://github.com/alice/teamfinder',
                status='open',
            )
            p1.participants.add(alice)
            p1.skills.add(proj_skill_py, proj_skill_dj)

            p2 = Project.objects.create(
                name='Мобильный трекер привычек',
                description='Приложение для отслеживания ежедневных целей',
                owner=bob,
                status='open',
            )
            p2.participants.add(bob)
            bob.favorites.add(p1)

        self.stdout.write(self.style.SUCCESS('Демо-данные готовы'))
        self.stdout.write(f'  alice@example.com / {DEMO_PASSWORD}')
        self.stdout.write(f'  bob@example.com / {DEMO_PASSWORD}')
