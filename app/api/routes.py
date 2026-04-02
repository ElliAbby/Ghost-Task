import time

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.api.deps import get_redis
from app.core.schemas import TaskCreate, TaskBase
from app.services.broker import TaskBroker


router =  APIRouter(prefix='/api/v1')


@router.post("/tasks")
async def create_task(data: TaskCreate, redis: Redis = Depends(get_redis)):
  broker = TaskBroker(redis)
  task = TaskBase(function_name=data.function_name, payload=data.payload)

  await broker.add_task(task, data.delay)
  return {
    "task_id": task.id,
    "status": "scheduled (created)",
  }


@router.get("/stats")
async def get_system_stats(redis: Redis = Depends(get_redis)):
  broker = TaskBroker(redis)
  stats = await broker.get_stats()

  # TODO: добавить информацию о "здоровье" системы
  return{
    "status": "online",
    "stats": stats,
    "server_time": time.time()
  }