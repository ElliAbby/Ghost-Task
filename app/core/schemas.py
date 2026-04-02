from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class TaskBase(BaseModel):
  id: UUID = Field(default_factory=uuid4)
  function_name: str
  payload: dict[str, Any] = Field(default_factory=dict)
  retries: int = 0


class TaskCreate(BaseModel):
  model_config = ConfigDict(extra='forbid')

  function_name: str
  payload: dict[str, Any] = Field(default_factory=dict)
  delay: int = Field(ge=0, description="Задержка в секундах")


class TaskResult(BaseModel):
  task_id: int
  status: str
  result: Optional[Any] = None
  error: Optional[str] = None