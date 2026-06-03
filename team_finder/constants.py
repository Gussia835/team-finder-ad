import re
from enum import StrEnum

DEFAULT_PAGE_SIZE = 12
MAX_SKILLS_AUTOCOMPLETE = 10

GITHUB_HOST = 'github.com'
PHONE_REGEX = re.compile(r'^(8\d{10}|\+7\d{10})$')

PROJECT_NAME_MAX_LENGTH = 200
PROJECT_SKILL_NAME_MAX_LENGTH = 124
PROJECT_STATUS_MAX_LENGTH = 6

USER_NAME_MAX_LENGTH = 124
USER_PHONE_MAX_LENGTH = 12
USER_ABOUT_MAX_LENGTH = 256

AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 80
AVATAR_DEFAULT_INITIAL = 'U'


class ProjectStatus(StrEnum):
    OPEN = 'open'
    CLOSED = 'closed'


PROJECT_STATUSES = [
    (ProjectStatus.OPEN, 'Open'),
    (ProjectStatus.CLOSED, 'Closed'),
]

PROJECT_STATUS_OPEN = ProjectStatus.OPEN
PROJECT_STATUS_CLOSED = ProjectStatus.CLOSED


class AvatarColor(StrEnum):
    MINT = '#A8DADC'
    STEEL_BLUE = '#457B9D'
    RED = '#E63946'
    CREAM = '#F1FAEE'
    SAGE = '#8AB17D'


AVATAR_COLORS = tuple(AvatarColor)


class QueryParam(StrEnum):
    SKILL = 'skill'
    FILTER = 'filter'
    PAGE = 'page'
    Q = 'q'


JSON_STATUS_OK = 'ok'
JSON_STATUS_ERROR = 'error'
JSON_KEY_STATUS = 'status'
JSON_KEY_ERROR = 'error'
JSON_KEY_FAVORITED = 'favorited'
JSON_KEY_PARTICIPANT = 'participant'
JSON_KEY_PROJECT_STATUS = 'project_status'
JSON_KEY_SKILL_ID = 'skill_id'
JSON_KEY_NAME = 'name'
JSON_KEY_CREATED = 'created'
JSON_KEY_ADDED = 'added'
