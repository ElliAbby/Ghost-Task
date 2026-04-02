import redis 
import json 
import time


client = redis.Redis(host='localhost', port=6379, decode_responses=True)

json_data = {
  "id": 101,
  "function": "send_welcome_email",
  "args": {"email": "user@example.com", "name": "Ivan"}
}

task_json = json.dumps(json_data)

now = time.time()
excute_at = now + 5

client.zadd("delayed_tasks", {task_json: excute_at})
print("Задача упакована в JSON и добавлена в план.")

while True:
    current_time = time.time()
    ready_tasks = client.zrangebyscore("delayed_tasks", 0, current_time, start=0, num=1)

    if ready_tasks:
        task_to_move = ready_tasks[0]
        client.zrem("delayed_tasks", task_to_move)
        client.lpush("ready_tasks", task_to_move)
        print("Оркестратор: Время пришло! Переложил задачу в конвейер.")
        break
    
    print("Оркестратор: Жду...")
    time.sleep(1)


print("Воркер: Жду задачу из конвейера...")
_, final_task_json = client.brpop("ready_tasks")
final_data = json.loads(final_task_json)
print(f"Воркер: Выполняю функцию {final_data['function']} для {final_data['args']['email']}")