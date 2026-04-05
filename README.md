# GhostTask: Distributed Task Scheduler (свой аналог Celery/Airflow)

GhostTask — это легковесный распределенный планировщик задач на Python, использующий Asyncio и Redis. Проект демонстрирует реализацию надежной очереди задач с поддержкой отложенного выполнения, автоматических повторов (retries) и мониторинга.

Суть: система, которая принимает задачи по API и выполняет их в заданное время или по расписанию.

Цель: Понять, как обеспечивать надежность в распределенных системах.

Особенность: не используются готовые библиотеки для задач (вроде Celery), а написано своё ядро на Asyncio, используя Redis как хранилище.

## Архитектура системы

Проект построен на базе микросервисного подхода и разделен на три независимых компонента, взаимодействующих через Redis:

- Producer (API): FastAPI сервис, принимающий задачи от пользователей и помещающий их в «зал ожидания» (Redis Sorted Set).
- Orchestrator: Процесс-диспетчер, который отслеживает время выполнения задач и атомарно перемещает готовые задачи в очередь исполнения (Redis List).
- Worker: Исполнитель, который по принципу FIFO забирает задачи из очереди, десериализует их и вызывает соответствующие Python-функции.

## Основные возможности

- Delayed Execution: Планирование задач на любое время в будущем (Unix Timestamp).
- Reliability & Retries: Система автоматических повторов с экспоненциальной задержкой (Exponential Backoff) при сбоях.
- Dead Letter Queue (DLQ): Изоляция задач, не выполненных после максимального количества попыток.
- Real-time Monitoring: Эндпоинт /stats для контроля состояния очередей.
- Graceful Shutdown: Безопасная остановка воркеров без потери текущих данных.
- Pydantic Validation: Строгая валидация схем данных на всех этапах.

## Стек технологий

- Language: Python 3.10+
- Framework: FastAPI
- Database (Queue/Storage): Redis 7.0+
- Concurrency: Asyncio
- Validation: Pydantic v2
- Infrastructure: Docker, Docker Compose

## Структура проекта

```text
ghost_task/
├── app/                # Основной пакет приложения
│   ├── __init__.py
│   ├── api/            # Всё, что касается HTTP (FastAPI)
│   │   ├── __init__.py
│   │   ├── routers/    # Эндпоинты
│   │   |   ├── __init__.py
│   │   |   ├── stats.py  # Статистика
│   │   |   └── tasks.py  # Задачи
│   │   └── deps.py     # Инъекция зависимостей (get_redis)
│   │
│   ├── core/           # Ядро системы (логика, которую делят все)
│   │   ├── __init__.py
│   │   ├── config.py   # Настройки (Pydantic Settings, .env)
│   │   ├── signals.py  # Настройки для верной отработки сочетания Ctrl+C
│   │   └── schemas.py  # Pydantic модели
│   │
│   ├── engine/         # Логика обработки
│   │   ├── __init__.py
│   │   ├── orchestrator.py # "Менеджер зала"
│   │   ├── worker.py       # "Повар"
│   │   ├── registry.py     # Класс для маппинга функций
│   │   └── tasks.py        # Список функций, которые умеет делать воркер
│   │
│   └── services/       # Бизнес-логика (Слой абстракции над Redis)
│       ├── __init__.py
│       └── broker.py    # Класс TaskBroker
│
├── tests/              # Папка для тестов
├── .env.example        # Пример переменных окружения
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt    # Зависимости
├── schema.excalidraw   # Схема объяснения принципа работы
├── main_api.py         # Точка входа для запуска FastAPI
└── main_engine.py      # Точка входа для запуска Воркеров
```

## Установка и запуск

1. Клонирование

```bash
git clone https://github.com/ElliAbby/Ghost-Task.git
cd Ghost-Task
```

2. Запуск инфраструктуры

Запуск:

```bash
docker-compose up -d
```

Остановка:

```bash
docker-compose down
```

<details>
<summary>Просмотр логов</summary>

1. Все логи всех сервисов:  
   `docker compose logs`

2. Смотреть логи в реальном времени:  
   `docker compose logs -f`

3. Логи только нужных сервисов:  
   `docker compose logs -f api engine redis`

4. Только последние N строк:  
   `docker compose logs --tail=100 api`  
   `docker compose logs --tail=200 engine`

5. Если нужен только один контейнер:  
`docker logs -f ghost_api`  
`docker logs -f ghost_engine`  
`docker logs -f ghost_redis`
</details>

## API Documentation

После запуска API доступно по адресу: http://127.0.0.1:8000

Interactive Docs (Swagger): http://127.0.0.1:8000/docs

Эндпоинты:

- `/tasks` - создать задачу
- `/tasls/available` - доступные функции
- `/stats` — информация о нагрузке на очереди

<details>
<summary>Пример запроса на создание задачи:</summary>

1. Для функции отправки письма

```json
POST /tasks
{
  "function_name": "send_email",
  "payload": {
    "email": "user@example.com",
    "name": "Ivan"
  },
  "delay": 5
}
```

2. Для функции синхронизации

```json
POST /tasks
{
  "function_name": "sync_data",
  "payload": {
    "user_id": 1
  },
  "delay": 60
}
```

3. Для функции оплаты

```json
POST /tasks
{
  "function_name": "process_payment",
  "payload": {
    "amount": 10,
    "currency": "RUB"
  },
  "delay": 60
}
```

</details>
