import redis
import time 


client = redis.Redis(host='localhost', port=6379, decode_responses=True)

now = time.time()
execute_at = now + 5
client.zadd('delayed_tasks', {'task_1': execute_at})

print(f"Задача добавлена. Сейчас: {now}. Выполнить в: {execute_at}")

while True:
  current_time = time.time()
  ready_tasks = client.zrangebyscore('delayed_tasks', 0, current_time)
  if ready_tasks:
    print(f"Найдена задача к исполнению: {ready_tasks[0]}")
    client.zrem('delayed_tasks', ready_tasks[0])
    break
  else:
    print("Задач нет. Проверяем ещё раз через 1 сек ...")
    time.sleep(1)