import asyncio
import logging 

from redis.asyncio import Redis

from app.core.config import config
from app.core.signals import stop_event, setup_signals
from app.services.broker import TaskBroker
from app.engine.orchestrator import orchestrator
from app.engine.worker import worker
from app.engine import tasks as _tasks  # noqa: F401


logger = logging.getLogger(__name__)


def setup_logging() -> None:
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
  )


async def main():
  redis = Redis.from_url(config.REDIS_URL, decode_responses=True)
  broker = TaskBroker(redis)
  logger.info(f"Engine запущен и слушает Redis...\nworkers={config.WORKER_COUNT}, redis={config.REDIS_URL}")

  setup_signals()

  worker_tasks = [worker(broker=broker, worker_id=i) for i in range(1, config.WORKER_COUNT + 1)]

  await asyncio.gather(
    orchestrator(broker),
    *worker_tasks
  )


if __name__ == "__main__":
  try:
    setup_logging()
    asyncio.run(main())
  except KeyboardInterrupt:
    logger.info("Выход...")