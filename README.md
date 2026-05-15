# Лабораторная работа №12: AI-ассистированная разработка

## Сведения о студенте

| Поле | Значение |
|------|----------|
| ФИО | Евстигнеев Фёдор Алексеевич |
| Группа | 220032-11 |
| Вариант | №5 (Система бронирования отелей) |
| Сложность | Средняя |
| Лабораторная работа | №12 |
| GitHub | https://github.com/FedorSwS/lab12-variant5 |

## Описание проекта

Веб-приложение для бронирования номеров в отеле.

### Технологии

- FastAPI + SQLAlchemy
- Pydantic валидация
- Pytest тесты
- Docker + PostgreSQL

## Запуск
docker-compose up --build

## Запуск тестов
pytest tests/ -v

## API Эндпоинты
### Customers
    POST /api/customers/ - создать

    GET /api/customers/ - список

    GET /api/customers/{id} - получить

    PUT /api/customers/{id} - обновить

    DELETE /api/customers/{id} - удалить

### Rooms
    POST /api/rooms/ - создать

    GET /api/rooms/ - список

    GET /api/rooms/available - доступные

    GET /api/rooms/{id} - получить

    PUT /api/rooms/{id} - обновить

    DELETE /api/rooms/{id} - удалить

### Bookings
    POST /api/bookings/ - создать

    GET /api/bookings/ - список

    GET /api/bookings/{id} - получить

    PUT /api/bookings/{id} - обновить

    DELETE /api/bookings/{id} - удалить

    GET /api/bookings/report/occupancy - отчёт загрузки

## Результаты тестов

tests/test_customers.py ..... PASSED
tests/test_rooms.py ..... PASSED
tests/test_bookings.py ......... PASSED
---------------------
19 passed in 2.34s