import asyncio
import logging

from app.engine.registry import register


logger = logging.getLogger(__name__)


@register.task(name='send_email')
async def send_email_welcome(email: str, name: str, **kwargs):
  logger.info(f"--- Отправка письма для {name} ({email}) ---")
  await asyncio.sleep(2)
  logger.info(f"--- Письмо для {name} ({email}) отправлено! ---")


@register.task(name='sync_data')
async def sync_user_data(user_id: int):
  logger.info(f"--- Синхронизация данных пользователя {user_id} ---")
  await asyncio.sleep(2)
  logger.info(f"--- Данные пользователя {user_id} синхронизированы! ---")


@register.task()
async def process_payment(amount: int, currency: str = "USD"):
    logger.info(f"Оплата на сумму {amount} {currency} принята")
    await asyncio.sleep(2)
    logger.info("Оплата успешно завершена")
