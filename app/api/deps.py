from fastapi import Depends, Request
from redis.asyncio import Redis

from app.services.broker import TaskBroker


def get_redis(request: Request) -> Redis:
  return request.app.state.redis


def get_broker(redis: Redis = Depends(get_redis)) -> TaskBroker:
  return TaskBroker(redis)