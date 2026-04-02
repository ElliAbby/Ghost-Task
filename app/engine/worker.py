import asyncio
import logging

from app.services.broker import TaskBroker
from app.core.schemas import TaskBase
from app.core.signals import stop_event
from app.engine.tasks import TASK_MAP

logger = logging.getLogger(__name__)


async def worker(broker: TaskBroker, worker_id: int):
  logger.info(f"[Worker {worker_id}] Запущен и ждет задач...")

  max_retries = 3

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
      
      await func(**task.payload)
      logger.info(f"[Worker {worker_id}] Готово!")
      # TODO: добавить статус выполнено

    except Exception as e:
      logger.info(f"Ошибка при выполнении задачи {task.id}: {e}")

      if task.retries < max_retries:
        # Рассчитываем задержку: чем больше попыток, тем дольше ждем (Exponential Backoff)
        retry_delay = (task.retries + 1) * 30

        logger.warning(f"Задача перепроверки {task.id}. Время для задержки: {retry_delay} (Попытка: {task.retries + 1})")
        await broker.retry_task(task, delay=retry_delay)
      else:
        logger.error(f"Задача {task.id} не может быть выполнена после {max_retries} попыток. Отменяем задачу.")
        await broker.move_to_dead_letter(task)
        # TODO: добавить статус отменено
  
  logger.info(f"[Worker {worker_id}] Завершил работу.")