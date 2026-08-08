import redis.asyncio as aioredis
from typing import AsyncGenerator

REDIS_URL = "redis://localhost:6379/0"

redis_client = aioredis.from_url(
    REDIS_URL,
    decode_responses=True,
    encoding="utf-8"
)

async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    # 直接返回 client，因为连接池会在后台自动管理连接
    yield redis_client