from datetime import timedelta

import aioredis
from fastapi import Depends, Security
from fastapi_auth0 import Auth0User

from app.core.auth0 import auth
from app.core.config import (
    REDIS_IP,
    REDIS_PORT,
    REDIS_RATELIMIT_PERIOD,
    REDIS_RATELIMIT_REQUESTS,
)

redisdb = aioredis.from_url(f"redis://{REDIS_IP}:{REDIS_PORT}")


async def get_redisdb() -> aioredis.Redis:
    return redisdb


def get_redis_ratelimit_config() -> tuple:
    return REDIS_RATELIMIT_REQUESTS, REDIS_RATELIMIT_PERIOD


async def is_ratelimited_redisdb(
    redisdb: aioredis.Redis, key: str, limit: int, period: timedelta
) -> bool:
    period_in_seconds = int(period.total_seconds())
    t = await redisdb.time()
    t = t[0]
    separation = round(period_in_seconds / limit)
    await redisdb.setnx(key, 0)
    get_t = await redisdb.get(key)
    tat = max(int(get_t), t)
    if tat - t <= period_in_seconds - separation:
        new_tat = max(tat, t) + separation
        await redisdb.set(key, new_tat)
        return False
    return True


async def check_user_ratelimit(
    redisdb: aioredis.Redis = Depends(get_redisdb),
    redis_ratelimit_config: tuple = Depends(get_redis_ratelimit_config),
    user: Auth0User = Security(auth.get_user, scopes=["use:all"]),
) -> tuple:
    is_ratelimited = await is_ratelimited_redisdb(
        redisdb, user.id, redis_ratelimit_config[0], redis_ratelimit_config[1]
    )
    return (user, is_ratelimited)
