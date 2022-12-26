![API YaMDB workflow](https://github.com/github/stas-chuprinskiy/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)


# API YaMDB - отзывы и рейтинги на любимые произведения

Проект YaMDb:

- хранит информацию о произведениях: название, категорию, дату создания и жанры;
- собирает текстовые отзывы пользователей на произведения;
- собирает комментарии к отзывам пользователей;
- формирует усредненную оценку произведений - их рейтинг.


### Реализация

Приложение и API реализованы в связке `Django` + `DRF`. Для развертывания и тестирования
проекта необходимо установить [Docker](https://docs.docker.com/engine/install/) и что-то,
что сможет отправлять запросы на сервер, например [httpie](https://httpie.io/docs/cli).

> 📘 Полная **документация к API** доступна после развертывания проекта по эндпойнту `/redoc/`.


### Установка

1. Клонируйте репозиторий:

```
git clone git@github.com:stas-chuprinskiy/infra_sp2.git
```

2. Перейдите в папку `infra/`. В файле `.env` определите параметры подключения к **postgres**:

```
# Настройки по умолчанию

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

3. Запустите проект:

```
docker-compose up -d
```

4. Выполните миграции:

```
docker-compose exec web python3 manage.py migrate
```

5. Создайте суперпользователя:

```
docker-compose exec web python3 manage.py createsuperuser
```

6. Соберите статические файлы проекта:

```
docker-compose exec web python3 manage.py collectstatic --no-input
```

7. Загрузите тестовые данные:

```
docker-compose exec web python3 manage.py loaddata fixtures.json
```

Проект станет доступен по адресу `localhost`.


### Пользовательские роли
* **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
* **Аутентифицированный пользователь (user)** — Аноним + публикация отзывов и комментариев.
* **Модератор (moderator)** — Аутентифицированный пользователь + удаление и редактирование
любых отзывов и комментариев.
* **Администратор (admin)** — полные права на управление контентом проекта.
* **Суперюзер Django** — перманентный администратор проекта, всегда обладает полными правами 
на управление контентом вне зависимости от роли.


### Алгоритм регистрации новых пользователей
1. Отправить POST-запрос с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`.
2. Получить код подтверждения `confirmation_code` на указанный адрес `email` (папка `sent_emails`).
	
	Просмотреть список отправленных сообщений в контейнере `web` можно с помощью команды:
	
	```
	docker-compose exec web ls /app/sent_emails
	```
	
	Вывести содержание письма в консоль:
	
	```
	docker-compose exec web cat /app/sent_emails/<Имя_лог_файла>
	```
	
3. Отправить POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`.
4. Получить JWT-токен.

После получения JWT-токена можно отправлять запросы к сервису.


### Тестирование API

Пример запроса создания нового отзыва:

```
http -v POST 127.0.0.1:8000/api/v1/titles/{title_id}/reviews/ Authorization:"Bearer {token}" text="New post!" score=10
```

```
{
    "id": id,
    "text": "New post!",
    "author": "author",
    "score": 10,
    "pub_date": "pub_date"
}
```

Пример запроса получения всех отзывов:

```
http -v GET 127.0.0.1:8000/api/v1/titles/{title_id}/reviews/ Authorization:"Bearer {token}"
```

```
[
    {
        "count": count,
        "next": "string",
        "previous": "string",
        "results": [
            {
                "id": id,
                "text": "New post!",
                "author": "author",
                "score": 10,
                "pub_date": "pub_date"
            },
            ...
        ]
    }
]
```

Пример запроса на удаление отзыва:

```
http -v DELETE 127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/ Authorization:"Bearer <your token>"
```
