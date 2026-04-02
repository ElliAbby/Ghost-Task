import redis

client = redis.Redis(host='localhost', port=6379, decode_responses=True)

client.set('test', 'Hello REDIS!')

value = client.get('test')
print(f"From Redis come: {value}")