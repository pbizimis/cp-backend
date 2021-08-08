from datetime import timedelta

import aioredis
from fastapi import Depends, Security
from fastapi_auth0 import Auth0User

from app.core.auth0 import auth
from app.core.config import (REDIS_IP, REDIS_PORT, REDIS_RATELIMIT_PERIOD,
                             REDIS_RATELIMIT_REQUESTS)

r = aioredis.from_url(f"redis://{REDIS_IP}:{REDIS_PORT}")

async def get_redis_db() -> aioredis.Redis:
    return r

def get_redis_ratelimit_config():
    return REDIS_RATELIMIT_REQUESTS, REDIS_RATELIMIT_PERIOD

async def request_is_limited(r, key: str, limit: int, period: timedelta):
    period_in_seconds = int(period.total_seconds())
    t = await r.time()
    t = t[0]
    separation = round(period_in_seconds / limit)
    await r.setnx(key, 0)
    get_t = await r.get(key)
    tat = max(int(get_t), t)
    if tat - t <= period_in_seconds - separation:
        new_tat = max(tat, t) + separation
        await r.set(key, new_tat)
        return False
    return True

async def check_user_ratelimit(r: aioredis.Redis = Depends(get_redis_db), rate_limit_config: tuple = Depends(get_redis_ratelimit_config), user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    is_ratelimited = await request_is_limited(r, user.id, rate_limit_config[0], rate_limit_config[1])
    return (user, is_ratelimited)