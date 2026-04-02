import logging

import uvicorn
from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from app.api.routes import router as api_router
from app.core.config import config


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
  app.state.redis = Redis.from_url(config.REDIS_URL, decode_responses=True)
  logger.info("API: Соединение с Redis установлено")
  yield
  await app.state.redis.close()
  logger.info("API: Соединение с Redis закрыто")


app = FastAPI(
  title="GhostTask API",
  description="Система распределенных отложенных задач",
  version="1.0.0",
  lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/")
async def root():
  return {"message": "Добро пожаловать в сервис Ghost Task"}


if __name__ == "__main__":
  uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)
