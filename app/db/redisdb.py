from datetime import timedelta

import aioredis
from fastapi import Depends, Security
from fastapi_auth0 import Auth0User

from app.core.auth0 import auth
from app.core.config import REDIS_RATELIMIT_PERIOD, REDIS_RATELIMIT_REQUESTS, REDIS_URL
from app.schemas.redisdb import RedisClient

redisdb = RedisClient()


def get_redis_ratelimit_config() -> tuple:
    """Get the redis ratelimit config."""
    return REDIS_RATELIMIT_REQUESTS, REDIS_RATELIMIT_PERIOD


async def is_ratelimited_redisdb(
    redisdb: aioredis.Redis, key: str, limit: int, period: timedelta
) -> bool:
    """Return if a ratelimit applies for the given key. This is an implementation of the Generic Cell Rate Algorithm.

    Args:
        redisdb (aioredis.Redis): the redisdb database connection
        key (str): the key (in this context the user auth0 id)
        limit (int): the limit of how often the function can be called for the same key
        period (timedelta): the period that resets the limit

    Returns:
        bool: a bool if the key is ratelimited
    """
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
    redisdb: aioredis.Redis = Depends(redisdb.get_client),
    redis_ratelimit_config: tuple = Depends(get_redis_ratelimit_config),
    user: Auth0User = Security(auth.get_user, scopes=["use:all"]),
) -> tuple:
    """Return if the user request is ratelimited.ArithmeticError

    Args:
        redisdb (aioredis.Redis, optional): the redisdb database connection. Defaults to Depends(redisdb.get_client).
        redis_ratelimit_config (tuple, optional): the ratelimit config for this application. Defaults to Depends(get_redis_ratelimit_config).
        user (Auth0User, optional): the current user object (decoded JWT). Defaults to Security(auth.get_user, scopes=["use:all"]).

    Returns:
        tuple: a tuple with the user object and the bool is a ratelimit applies
    """
    is_ratelimited = await is_ratelimited_redisdb(
        redisdb, user.id, redis_ratelimit_config[0], redis_ratelimit_config[1]
    )
    return (user, is_ratelimited)
