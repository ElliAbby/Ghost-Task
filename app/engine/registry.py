import logging
from typing import Callable


logger = logging.getLogger(__name__) 


class TaskRegistry:
  def __init__(self):
    self._tasks: dict[str, Callable] = {}

  def task(self, name: str | None = None):
    def decorator(func: Callable):
      task_name = name or func.__name__
      if task_name in self._tasks:
        logger.warning(f"Task {task_name} уже зарегистрирован и будет перезаписана!")
      self._tasks[task_name] = func
      return func
    return decorator
  
  def get_task(self, name: str) -> Callable | None:
    return self._tasks.get(name)

  def list_tasks(self) -> list[str]:
    return list(self._tasks.keys())
  

register = TaskRegistry()