import asyncio


async def send_email_welcome(email: str, name: str, **kwargs):
  print(f"--- Отправка письма для {name} ({email}) ---")
  await asyncio.sleep(2)
  print(f"--- Письмо для {name} ({email}) отправлено! ---")


async def sync_user_data(user_id: int):
  print(f"--- Синхронизация данных пользователя {user_id} ---")
  await asyncio.sleep(2)
  print(f"--- Данные пользователя {user_id} синхронизированы! ---")


TASK_MAP = {
  "send_email": send_email_welcome,
  "sync_data": sync_user_data,
}