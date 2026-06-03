from enum import StrEnum

from team_finder.constants import DEFAULT_PAGE_SIZE

USERS_PER_PAGE = DEFAULT_PAGE_SIZE

TEMPLATE_PARTICIPANTS = 'users/participants.html'
TEMPLATE_USER_DETAILS = 'users/user-details.html'
TEMPLATE_REGISTER = 'users/register.html'
TEMPLATE_LOGIN = 'users/login.html'
TEMPLATE_EDIT_PROFILE = 'users/edit_profile.html'
TEMPLATE_CHANGE_PASSWORD = 'users/change_password.html'

MESSAGE_REGISTER_SUCCESS = 'Регистрация успешна! Войдите в аккаунт.'
MESSAGE_LOGIN_SUCCESS = 'Добро пожаловать!'
MESSAGE_LOGOUT = 'Вы вышли из аккаунта'
MESSAGE_PROFILE_UPDATED = 'Профиль обновлён'
MESSAGE_PASSWORD_CHANGED = 'Пароль изменён'

DEMO_PASSWORD = 'demo12345'
DEMO_ALICE_EMAIL = 'alice@example.com'
DEMO_BOB_EMAIL = 'bob@example.com'
DEMO_PROJECT_TEAMFINDER = 'TeamFinder Clone'
DEMO_PROJECT_HABITS = 'Мобильный трекер привычек'


class UserFilterType(StrEnum):
    OWNERS_OF_FAVORITE_PROJECTS = 'owners-of-favorite-projects'
    OWNERS_OF_PARTICIPATING_PROJECTS = 'owners-of-participating-projects'
    INTERESTED_IN_MY_PROJECTS = 'interested-in-my-projects'
    PARTICIPANTS_OF_MY_PROJECTS = 'participants-of-my-projects'
