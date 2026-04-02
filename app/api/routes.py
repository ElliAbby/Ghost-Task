import time

from fastapi import APIRouter, Depends

from app.api.deps import get_broker
from app.core.schemas import TaskCreate, TaskBase
from app.services.broker import TaskBroker


router =  APIRouter(prefix='/api/v1')


@router.post("/tasks")
async def create_task(data: TaskCreate, broker: TaskBroker = Depends(get_broker)):
  task = TaskBase(function_name=data.function_name, payload=data.payload)

  await broker.add_task(task, data.delay)
  return {
    "task_id": task.id,
    "status": "scheduled (created)",
  }


@router.get("/stats")
async def get_system_stats(broker: TaskBroker = Depends(get_broker)):
  stats = await broker.get_stats()

  # TODO: добавить информацию о "здоровье" системы
  return{
    "status": "online",
    "stats": stats,
    "server_time": time.time()
  }