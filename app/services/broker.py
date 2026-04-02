import json 
import time

from redis.asyncio import Redis

from app.core.schemas import TaskBase
from app.core.config import config


class TaskBroker:
  def __init__(self, redis: Redis):
    self.redis = redis
    self.delayed_key = config.DELAYED_KEY
    self.executing_key = config.EXECUTING_KEY
    self.dead_letter_key = config.DEAD_LETTER_KEY

  async def add_task(self, task: TaskBase, delay: int):
    '''Добавление задачи в очередь с задержкой'''
    execute_at = time.time() + delay
    task_json = task.model_dump_json()
    await self.redis.zadd(self.delayed_key, {task_json: execute_at})

  async def get_next_ready_task(self) -> str | None:
    '''Оркестратор: ищет одну готовую задачу и возвращает её JSON'''
    now = time.time()
    tasks = await self.redis.zrangebyscore(self.delayed_key, 0, now, start=0, num=1)
    return tasks[0] if tasks else None
  
  async def move_to_execution(self, task_json: str):
    '''Перемещение задачи из задержанной в выполняемую очередь'''
    async with self.redis.pipeline(transaction=True) as pipe:
      await pipe.zrem(self.delayed_key, task_json)
      await pipe.lpush(self.executing_key,task_json)
      await pipe.execute()
  
  async def move_to_dead_letter(self, task: TaskBase):
    '''Перемещение задачи в мертвую очередь'''
    task_json = task.model_dump_json()
    await self.redis.lpush(self.dead_letter_key, task_json)

  async def fetch_task(self, timeout: int = 5) -> TaskBase | None:
    '''Работник: забирает задачу из выполняемой очереди'''
    res = await self.redis.brpop(self.executing_key, timeout=timeout)
    if res:
      _, task_json = res
      return TaskBase.model_validate_json(task_json)

    return None
  
  async def retry_task(self, task: TaskBase, delay: int = 30):
    '''Повторная попытка выполнения задачи'''
    task.retries += 1
    await self.add_task(task, delay=delay)

  async def get_stats(self) -> dict:
    '''Возвращает количество задач в каждой очереди'''
    delayed_count = await self.redis.zcard(self.delayed_key)
    execution_count = await self.redis.llen(self.executing_key)
    dead_count = await self.redis.llen(self.dead_letter_key)

    return {
      "pending_in_scheduler": delayed_count,  # Ждут своего времени
      "ready_for_execution": execution_count,  # В очереди на воркер
      "dead_letter_queue": dead_count,  # Не выполненные задачи
    }
