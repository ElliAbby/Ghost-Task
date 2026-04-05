"""
Тесты валидации payload для разных типов задач.

Запуск:
    pytest tests/test_validation.py -v
"""

import pytest
from pydantic import ValidationError

from app.core.schemas import (
  TaskCreate,
  SendEmailPayload,
  SyncDataPayload,
  PAYLOAD_SCHEMAS,
)
from app.engine.tasks import TASK_MAP


# ── Вспомогательные фабрики ───────────────────────────────────────────────────

def make_send_email(**overrides):
  return {
    "function_name": "send_email",
    "payload": {"email": "user@example.com", "name": "Ivan"},
    "delay": 5,
    **overrides,
  }


def make_sync_data(**overrides):
  return {
    "function_name": "sync_data",
    "payload": {"user_id": 42},
    "delay": 0,
    **overrides,
  }


# ── PAYLOAD_SCHEMAS согласованы с TASK_MAP ────────────────────────────────────

class TestTaskMapConsistency:
  def test_every_payload_schema_has_handler(self):
    missing = PAYLOAD_SCHEMAS.keys() - TASK_MAP.keys()
    assert not missing, f"Нет обработчика для: {missing}"

  def test_every_handler_has_payload_schema(self):
    missing = TASK_MAP.keys() - PAYLOAD_SCHEMAS.keys()
    assert not missing, f"Нет payload-схемы для: {missing}"


# ── send_email: позитивные кейсы ──────────────────────────────────────────────

class TestSendEmailValid:
  def test_basic(self):
    task = TaskCreate.model_validate(make_send_email())
    assert task.function_name == "send_email"
    assert task.payload["email"] == "user@example.com"
    assert task.payload["name"] == "Ivan"

  def test_email_normalized(self):
    # EmailStr нормализует адрес (lowercase домен)
    task = TaskCreate.model_validate(
      make_send_email(payload={"email": "User@Example.COM", "name": "Test"})
    )
    assert "@example.com" in task.payload["email"]

  def test_delay_zero(self):
    task = TaskCreate.model_validate(make_send_email(delay=0))
    assert task.delay == 0

  def test_delay_large(self):
    task = TaskCreate.model_validate(make_send_email(delay=86400))
    assert task.delay == 86400


# ── send_email: негативные кейсы ──────────────────────────────────────────────

class TestSendEmailInvalid:
  def test_missing_email(self):
    with pytest.raises(ValidationError) as exc_info:
      TaskCreate.model_validate(
        make_send_email(payload={"name": "Ivan"})
      )
    assert "email" in str(exc_info.value)

  def test_invalid_email_format(self):
    with pytest.raises(ValidationError) as exc_info:
      TaskCreate.model_validate(
        make_send_email(payload={"email": "not-an-email", "name": "Ivan"})
      )
    assert "email" in str(exc_info.value)

  def test_missing_name(self):
    with pytest.raises(ValidationError) as exc_info:
      TaskCreate.model_validate(
        make_send_email(payload={"email": "user@example.com"})
      )
    assert "name" in str(exc_info.value)

  def test_empty_name(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate(
        make_send_email(payload={"email": "user@example.com", "name": ""})
      )

  def test_name_too_long(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate(
        make_send_email(payload={"email": "user@example.com", "name": "x" * 101})
      )

  def test_extra_field_forbidden(self):
    with pytest.raises(ValidationError) as exc_info:
      TaskCreate.model_validate(
        make_send_email(
          payload={"email": "user@example.com", "name": "Ivan", "extra": "oops"}
        )
      )
    assert "extra" in str(exc_info.value)

  def test_wrong_payload_type(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate(make_send_email(payload="not-a-dict"))

  def test_negative_delay(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate(make_send_email(delay=-1))


# ── sync_data: позитивные кейсы ───────────────────────────────────────────────

class TestSyncDataValid:
  def test_basic(self):
    task = TaskCreate.model_validate(make_sync_data())
    assert task.function_name == "sync_data"
    assert task.payload["user_id"] == 42

  def test_user_id_one(self):
    task = TaskCreate.model_validate(make_sync_data(payload={"user_id": 1}))
    assert task.payload["user_id"] == 1


# ── sync_data: негативные кейсы ───────────────────────────────────────────────

class TestSyncDataInvalid:
  def test_missing_user_id(self):
    with pytest.raises(ValidationError) as exc_info:
      TaskCreate.model_validate(make_sync_data(payload={}))
    assert "user_id" in str(exc_info.value)

  def test_user_id_zero(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate(make_sync_data(payload={"user_id": 0}))

  def test_user_id_negative(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate(make_sync_data(payload={"user_id": -5}))

  def test_user_id_wrong_type(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate(make_sync_data(payload={"user_id": "abc"}))

  def test_extra_field_forbidden(self):
    with pytest.raises(ValidationError) as exc_info:
      TaskCreate.model_validate(
        make_sync_data(payload={"user_id": 1, "secret": "leak"})
      )
    assert "secret" in str(exc_info.value)


# ── Неподдерживаемый function_name ────────────────────────────────────────────

class TestUnknownFunctionName:
  def test_unknown_function_rejected(self):
    with pytest.raises(ValidationError) as exc_info:
      TaskCreate.model_validate({
        "function_name": "delete_all_data",
        "payload": {},
        "delay": 0,
      })
    assert "function_name" in str(exc_info.value)

  def test_empty_function_name_rejected(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate({
        "function_name": "",
        "payload": {},
        "delay": 0,
      })

  def test_extra_top_level_field_forbidden(self):
    with pytest.raises(ValidationError):
      TaskCreate.model_validate({
        "function_name": "send_email",
        "payload": {"email": "user@example.com", "name": "Ivan"},
        "delay": 0,
        "injected": "bad",
      })


# ── Прямая валидация payload-схем ────────────────────────────────────────────

class TestPayloadSchemasDirectly:
  def test_send_email_payload_valid(self):
    p = SendEmailPayload(email="a@b.com", name="Alice")
    assert p.name == "Alice"

  def test_sync_data_payload_valid(self):
    p = SyncDataPayload(user_id=99)
    assert p.user_id == 99

  def test_send_email_payload_extra_forbidden(self):
    with pytest.raises(ValidationError):
      SendEmailPayload(email="a@b.com", name="Alice", role="admin")

  def test_sync_data_payload_extra_forbidden(self):
    with pytest.raises(ValidationError):
      SyncDataPayload(user_id=1, extra="oops")
