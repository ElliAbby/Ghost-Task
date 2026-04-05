import time

from fastapi import APIRouter, Depends

from app.api.deps import get_broker
from app.services.broker import TaskBroker


router = APIRouter(prefix='/stats', tags=['Statistics & Analytics'])


@router.get('/')
async def get_system_stats(broker: TaskBroker = Depends(get_broker)):
  stats = await broker.get_stats()

  # TODO: добавить информацию о "здоровье" системы
  return{
    "status": "online",
    "stats": stats,
    "server_time": time.time()
  }