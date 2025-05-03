import os
from databases import Database
import aioredis
from dotenv import load_dotenv

load_dotenv()  # Load from .env file in backend directory

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tint_system")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

database = Database(DATABASE_URL)
redis_pool = None

async def connect_db():
    await database.connect()
    global redis_pool
    redis_pool = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

async def disconnect_db():
    await database.disconnect()
    if redis_pool:
        await redis_pool.close()

def get_redis():
    if not redis_pool:
        raise Exception("Redis connection not initialized")
    return redis_pool