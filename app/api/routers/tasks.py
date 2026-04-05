from fastapi import APIRouter, Depends

from app.api.deps import get_broker
from app.core.schemas import TaskCreate, TaskBase
from app.services.broker import TaskBroker
from app.engine.registry import register
from app.engine import tasks as _tasks  # noqa: F401


router =  APIRouter(prefix='/tasks', tags=['Tasks'])


@router.post('/')
async def create_task(data: TaskCreate, broker: TaskBroker = Depends(get_broker)):
  task = TaskBase(function_name=data.function_name, payload=data.payload)

  await broker.add_task(task, data.delay)
  return {
    "task_id": task.id,
    "status": "scheduled (created)",
  }


@router.get('/available')
async def get_available_tasks():
  return {"available_tasks": register.list_tasks()}