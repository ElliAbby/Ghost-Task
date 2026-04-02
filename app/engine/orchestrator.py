import asyncio
import logging

from app.services.broker import TaskBroker
from app.core.signals import stop_event


logger = logging.getLogger(__name__)


async def orchestrator(broker: TaskBroker):
  logger.info("[Orchestrator] запущен и ждёт готовых задач...")

  while not stop_event.is_set():
    try:
      ready_tasks = await broker.get_next_ready_task()

      if ready_tasks:
        # task_json = ready_tasks[0]
        await broker.move_to_execution(ready_tasks)
        logger.info(f"[Orchestrator] Задача отправлена в конвейер: {ready_tasks}")

      await asyncio.sleep(0.5)

    except Exception as e:
      logger.error(f"[Orchestrator] Ошибка: {e}")
      await asyncio.sleep(1)
