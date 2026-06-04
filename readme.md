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

| Вариант | Функции                                                |
| ------- | ------------------------------------------------------ |
| 1       | Избранные проекты, фильтры участников                  |
| 2       | Навыки пользователей, фильтр участников по навыку      |
| 3       | Необходимые навыки проектов, фильтр проектов по навыку |

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

| Переменная          | Описание                                                                                           |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| `DJANGO_SECRET_KEY` | Секретный ключ Django                                                                              |
| `DJANGO_DEBUG`      | `True` для разработки                                                                              |
| `TASK_VERSION`      | Номер варианта шаблонов: `1`, `2` или `3`                                                          |
| `POSTGRES_DB`       | Имя базы данных                                                                                    |
| `POSTGRES_USER`     | Пользователь PostgreSQL                                                                            |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL                                                                                  |
| `POSTGRES_HOST`     | `localhost` локально, `db` в Docker web                                                            |
| `POSTGRES_PORT`     | Порт PostgreSQL (по умолчанию `5432`)                                                              |
| `ALLOWED_HOSTS`     | Список разрешённых хостов, разделённых запятой (по умолчанию localhost,127.0.0.1,[::1],testserver) |

## Запуск через Docker Compose

```bash
docker compose up --build -d
docker compose exec web python manage.py load_demo_data
```

Приложение: [http://localhost:8000](http://localhost:8000)

**Не запускайте** `python manage.py runserver` одновременно с контейнером `web` — на Windows это даёт конфликт порта 8000 и ошибки 404 на `127.0.0.1`.

Демо-аккаунты:

| Email             | Пароль    |
| ----------------- | --------- |
| alice@example.com | demo12345 |
| bob@example.com   | demo12345 |

## REST API

### Доступные эндпоинты

- `/api/v1/projects/` — список проектов, создание/изменение/удаление.
- `/api/v1/users/` — список пользователей, просмотр профиля.
- `/api/v1/projects/{id}/toggleFavorite/` — добавить/удалить проект из избранного.
- `/api/v1/projects/{id}/skills/` — автокомплит навыков проекта.
- `/api/v1/users/{id}/skills/` — автокомплит навыков пользователя.
- `/api/v1/projects/{id}/skills/add/` — добавить навык к проекту.
- `/api/v1/users/{id}/skills/add/` — добавить навык пользователю.
- `/api/v1/projects/{id}/skills/{skill_id}/remove/` — удалить навык у проекта.
- `/api/v1/users/{id}/skills/{skill_id}/remove/` — удалить навык у пользователя.

Для доступа к эндпоинтам, требующим авторизации, необходимо передавать токен сессии или использовать аутентификацию через сессию в браузере.

## Локальная разработка

```bash
docker compose up -d db
pip install -r requirements.txt
python manage.py migrate
python manage.py load_demo_data
python manage.py runserver
```

## Тесты

PostgreSQL должен быть запущен, а пароль в `.env` должен **совпадать** с тем, с которым был создан контейнер `db`. Иначе будет `password authentication failed`.

```bash
docker compose up -d db
python manage.py test
```

Если пароль в `.env` меняли после первого запуска, пересоздайте volume:

```bash
docker compose down -v
docker compose up -d db
python manage.py migrate
python manage.py test
```

CI: `.github/workflows/ci.yml`

## Автор

Дмитрий Федотов
📧 fdtvdmitriy@gmail.com
🔗 [GitHub](https://github.com/Gussia835)
