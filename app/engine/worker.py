import asyncio
import logging

from pydantic import ValidationError

from app.services.broker import TaskBroker
from app.core.schemas import TaskBase, PAYLOAD_SCHEMAS
from app.core.signals import stop_event
from app.core.config import config
from app.engine.tasks import TASK_MAP

logger = logging.getLogger(__name__)


def _assert_task_map_complete() -> None:
  """Проверяет, что для каждой зарегистрированной схемы есть обработчик."""
  missing = PAYLOAD_SCHEMAS.keys() - TASK_MAP.keys()
  if missing:
    raise RuntimeError(
      f"TASK_MAP не содержит обработчиков для: {missing}. "
      "Добавьте обработчик или удалите схему из PAYLOAD_SCHEMAS."
    )


async def worker(broker: TaskBroker, worker_id: int):
  _assert_task_map_complete()
  logger.info(f"[Worker {worker_id}] Запущен и ждет задач...")

  while not stop_event.is_set():
    try:
      task: TaskBase = await broker.fetch_task(timeout=5)
      if not task:
        continue

      logger.info(f"[Worker {worker_id}] Выполняю: {task.id}: {task.function_name}...")

      func = TASK_MAP.get(task.function_name)
      if not func:
        logger.error(f"Неизвестная функция: {task.function_name}")
        await broker.move_to_dead_letter(task)
        continue

      # Повторная валидация payload (защита от данных, попавших в очередь
      # в обход API, например при ручном вмешательстве или ретраях)
      schema = PAYLOAD_SCHEMAS.get(task.function_name)
      if schema:
        try:
          validated_payload = schema.model_validate(task.payload)
        except ValidationError as exc:
          logger.error(
            f"[Worker {worker_id}] Невалидный payload задачи {task.id}: {exc}"
          )
          await broker.move_to_dead_letter(task)
          continue
        await func(**validated_payload.model_dump())
      else:
        await func(**task.payload)

      logger.info(f"[Worker {worker_id}] Готово!")
      # TODO: добавить статус выполнено

    except Exception as e:
      logger.info(f"Ошибка при выполнении задачи {task.id}: {e}")

      if task.retries < config.MAX_RETRIES:
        # Рассчитываем задержку: чем больше попыток, тем дольше ждем (Exponential Backoff)
        retry_delay = (task.retries + 1) * 5

        logger.warning(f"Задача перепроверки {task.id}. Время для задержки: {retry_delay} (Попытка: {task.retries + 1})")
        await broker.retry_task(task, delay=retry_delay)
      else:
        logger.error(f"Задача {task.id} не может быть выполнена после {config.MAX_RETRIES} попыток. Отменяем задачу.")
        await broker.move_to_dead_letter(task)
        # TODO: добавить статус отменено
  
  logger.info(f"[Worker {worker_id}] Завершил работу.")