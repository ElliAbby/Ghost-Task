import logging

import uvicorn
from fastapi import FastAPI
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from app.api.routers.tasks import router as tasks_router
from app.api.routers.stats import router as stats_router
from app.core.config import config


logger = logging.getLogger(__name__)


def setup_logging() -> None:
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
  )


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
  prefix="/api/v1",
  lifespan=lifespan,
)

app.include_router(tasks_router)
app.include_router(stats_router)


@app.get("/")
async def root():
  return {"message": "Добро пожаловать в сервис Ghost Task"}


if __name__ == "__main__":
  setup_logging()
  uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)
