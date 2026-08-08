import redis
redis_client = redis.from_url("redis://localhost:6379/0",
               encoding="utf-8",
               decode_responses=True)

redis_client.set("code1","python")

# redis_client.set(name="code2",value="python2",ex=60)

code = redis_client.get("code1")
print(code)

redis_client.delete("code1")
code = redis_client.get("code1")
print(code)