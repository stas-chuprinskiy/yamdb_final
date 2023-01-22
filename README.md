[![API YaMDB workflow](https://github.com/stas-chuprinskiy/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/stas-chuprinskiy/yamdb_final/actions/workflows/yamdb_workflow.yml)


# API YaMDB - отзывы и рейтинги на любимые произведения

YaMDb - пользовательские отзывы, оценки и комментарии к любимым произведениям. 


### Технологии

* Python 3.10
* Django 4.1
* DjangoRestFramework 3.14


### Приложение

Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». 
Список категорий может быть расширен. Каждому произведению может быть 
присвоен жанр из списка предустановленных.

Пользователи оставляют к произведениям текстовые отзывы и ставят оценки. 
Из оценок формируется усреднённая оценка — рейтинг произведения. 
На одно произведение пользователь может оставить только один отзыв и оценку.

Каждый отзыв может быть прокомментирован любым пользователем сервиса.


### Установка

> Для развертывания и тестирования проекта необходимо установить 
[Docker](https://docs.docker.com/engine/install/)

- Клонируйте репозиторий
```
git clone <link>
```

- Перейдите в папку `infra/`. В файле `.env` определите параметры 
подключения к **postgres**
```
# Настройки по умолчанию

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

- Запустите проект
```
docker-compose up -d
```

- Примените миграции
```
docker-compose exec web python3 manage.py migrate
```

- Создайте суперпользователя
```
docker-compose exec web python3 manage.py createsuperuser
```

- Соберите статические файлы проекта
```
docker-compose exec web python3 manage.py collectstatic --no-input
```

- Загрузите тестовые данные
```
docker-compose exec web python3 manage.py loaddata fixtures.json
```

Проект станет доступен по адресу `localhost`.


### Список доступных эндпойнтов

* `auth` - аутентификация пользователей;
* `users` - управление пользователями;
* `titles` - произведения;
* `categories` - категории (типы) произведений;
* `genres` - жанры произведений;
* `reviews` - отзывы к произведениям;
* `comments` - комментарии к отзывам.

Полная документация доступна после запуска проекта по адресу: 
**<localhost или ip>/redoc/**.


### Пользовательские роли

- **Аноним** — просмотр описаний произведений, чтение отзывов и комментариев.
- **Аутентифицированный пользователь (user)** — Аноним + публикация отзывов 
и комментариев.
- **Модератор (moderator)** — Аутентифицированный пользователь + удаление и 
редактирование любых отзывов и комментариев.
- **Администратор (admin)** — полные права на управление контентом проекта.
- **Суперюзер Django** — перманентный администратор проекта, всегда обладает 
полными правами вне зависимости от роли.


### Алгоритм регистрации новых пользователей

1. Отправка POST-запроса с параметрами `email` и `username` на эндпоинт 
`/api/v1/auth/signup/`.
2. Получение кода подтверждения `confirmation_code` на указанный адрес 
`email` (папка `sent_emails`).
    - Просмотр отправленных сообщений в контейнере `web`:
	```
	docker-compose exec web ls /app/sent_emails
	```
	
	- Вывод содержания письма в консоль:
	```
	docker-compose exec web cat /app/sent_emails/<Имя_лог_файла>
	```
3. Отправка POST-запроса с параметрами `username` и `confirmation_code` 
на эндпоинт `/api/v1/auth/token/`.
4. Получение JWT-токена.

После получения JWT-токена можно отправлять запросы к сервису.


### Тестирование API

Вы можете отправлять запросы к API любым удобным для вас способом. 
В примерах ниже для отправки запросов используется библиотека `httpie`. 
Подробней о `httpie` вы можете узнать в [документации](https://httpie.io/docs/cli).

**Signup**
```
http -v POST 127.0.0.1:8000/api/v1/auth/signup/
email="<email>" username="<username>" password="<password>"
```

Будет отправлен `confirmation_code` на почту (см. папку `sent_emails`)

**Получение JWT-токена**
```
http -v POST 127.0.0.1:8000/api/v1/auth/token/
username="<username>" confirmation_code="<confirmation_code>"
```

```
{
    "token": "<token>"
}
```

**Cоздание отзыва**
```
http -v POST 127.0.0.1:8000/api/v1/titles/
Authorization:"Bearer <token>" 
name="New title" year="2020" genre=["comedy"] category="movie"
```

```
{
    "id": 33,
    "name": "New title",
    "year": 2020,
    "description": "",
    "genre": [
        "comedy"
    ],
    "category": "movie"
}
```

**Обновление отзыва**
```
http -v PATCH 127.0.0.1:8000/api/v1/titles/{title_id}/
Authorization:"Bearer <token>" 
year="2021"
```

```
{
    "id": 33,
    "name": "New title",
    "year": 2021,
    "description": "",
    "genre": [
        "comedy"
    ],
    "category": "movie"
}
```

**Получение всех отзывов**
```
http -v GET 127.0.0.1:8000/api/v1/titles/
Authorization:"Bearer <token>" 
```

```
{
    "count": 33,
    "next": "http://localhost:8000/api/v1/titles/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Побег из Шоушенка",
            "year": 1994,
            "rating": 10,
            "description": "",
            "genre": [
                {
                    "name": "Драма",
                    "slug": "drama"
                }
            ],
            "category": {
                "name": "Фильм",
                "slug": "movie"
            }
        },
        ...
        {}
    ]
}
```

**Удаление отзыва**
```
http -v DELETE 127.0.0.1:8000/api/v1/titles/{title_id}/ 
Authorization:"Bearer <token>"
```


### Автор

*Чупринский Станислав*
