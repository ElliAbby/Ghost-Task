import asyncio
import signal


stop_event = asyncio.Event()


def heandle_exit():
  '''Функция, которая сработает при нажатии Ctrl+C'''
  print("\n[System] Получен сигнал остановки. Завершаем работу...")
  stop_event.set()


def setup_signals():
  '''Регистрируем обработчики сигналов в текущем цикле событий'''
  loop = asyncio.get_running_loop()

  for sig in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(sig, heandle_exit)