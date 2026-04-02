import asyncio
import logging 

from redis.asyncio import Redis

from app.core.config import config
from app.core.signals import stop_event, setup_signals
from app.services.broker import TaskBroker
from app.engine.orchestrator import orchestrator
from app.engine.worker import worker


logging.basicConfig(level=logging.INFO)


async def main():
  redis = Redis.from_url(config.REDIS_URL, decode_responses=True)
  broker = TaskBroker(redis)
  print("Engine запущен и слушает Redis...")

  setup_signals()

  await asyncio.gather(
    orchestrator(broker),
    worker(broker=broker, worker_id=1),
    worker(broker=broker, worker_id=2),
    worker(broker=broker, worker_id=3),
  )


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    print("Выход...")