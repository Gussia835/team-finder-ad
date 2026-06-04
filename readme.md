# TeamFinder

Веб-платформа для поиска команды на pet-проекты: разработчики, дизайнеры и другие специалисты публикуют идеи, откликаются на проекты и находят единомышленников.

## Возможности

- Регистрация и вход по email
- Публичные профили с контактами, навыками и списком проектов
- Создание, редактирование и завершение проектов
- Участие в чужих проектах
- Постраничные списки проектов и участников (12 элементов на страницу)
- REST API (`/api/v1/`) для проектов и пользователей

Дополнительно по варианту задания (`TASK_VERSION` в `.env`):

| Вариант | Функции |
|---------|---------|
| 1 | Избранные проекты, фильтры участников |
| 2 | Навыки пользователей, фильтр участников по навыку |
| 3 | Необходимые навыки проектов, фильтр проектов по навыку |

## Стек

- Python 3.12
- Django 5.2
- Django REST Framework
- PostgreSQL 16
- Docker, Docker Compose
- Pillow (аватары)
- GitHub Actions (CI)

## Переменные окружения

Скопируйте `.env_example` в `.env`:

```bash
cp .env_example .env
```

| Переменная | Описание |
|------------|----------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django |
| `DJANGO_DEBUG` | `True` для разработки |
| `TASK_VERSION` | Номер варианта шаблонов: `1`, `2` или `3` |
| `POSTGRES_DB` | Имя базы данных |
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_HOST` | `localhost` локально, `db` в Docker web |
| `POSTGRES_PORT` | Порт PostgreSQL (по умолчанию `5432`) |

## Запуск через Docker Compose

```bash
docker compose up --build -d
docker compose exec web python manage.py load_demo_data
```

Приложение: [http://localhost:8000](http://localhost:8000)

**Не запускайте** `python manage.py runserver` одновременно с контейнером `web` — на Windows это даёт конфликт порта 8000 и ошибки 404 на `127.0.0.1`.

Демо-аккаунты:

| Email | Пароль |
|-------|--------|
| alice@example.com | demo12345 |
| bob@example.com | demo12345 |

## Локальная разработка

```bash
docker compose up -d db
pip install -r requirements.txt
python manage.py migrate
python manage.py load_demo_data
python manage.py runserver
```

## Тесты

```bash
python manage.py test
```

CI: `.github/workflows/ci.yml`
