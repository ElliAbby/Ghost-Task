from typing import Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, EmailStr, model_validator
from uuid import UUID, uuid4


# ── Payload schemas ───────────────────────────────────────────────────────────

class SendEmailPayload(BaseModel):
  """Payload для задачи send_email."""
  model_config = ConfigDict(extra='forbid')

  email: EmailStr
  name: str = Field(min_length=1, max_length=100)


class SyncDataPayload(BaseModel):
  """Payload для задачи sync_data."""
  model_config = ConfigDict(extra='forbid')

  user_id: int = Field(gt=0)


# Реестр: function_name → класс схемы payload.
# При добавлении новой задачи достаточно добавить запись сюда.
PAYLOAD_SCHEMAS: dict[str, type[BaseModel]] = {
  "send_email": SendEmailPayload,
  "sync_data": SyncDataPayload,
}

# Литеральный тип — список допустимых имён функций
FunctionName = Literal["send_email", "sync_data"]


# ── Core models ───────────────────────────────────────────────────────────────

class TaskBase(BaseModel):
  id: UUID = Field(default_factory=uuid4)
  function_name: str
  payload: dict[str, Any] = Field(default_factory=dict)
  retries: int = 0


class TaskCreate(BaseModel):
  model_config = ConfigDict(extra='forbid')

  function_name: FunctionName
  payload: dict[str, Any] = Field(default_factory=dict)
  delay: int = Field(ge=0, description="Задержка в секундах")

  @model_validator(mode='after')
  def validate_payload_for_function(self) -> 'TaskCreate':
    """Валидирует payload согласно схеме конкретного типа задачи."""
    schema = PAYLOAD_SCHEMAS[self.function_name]
    validated = schema.model_validate(self.payload)
    # Сохраняем только явно объявленные поля (лишние поля уже отклонены схемой)
    self.payload = validated.model_dump()
    return self


class TaskResult(BaseModel):
  task_id: int
  status: str
  result: Optional[Any] = None
  error: Optional[str] = None