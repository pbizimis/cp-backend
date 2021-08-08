from app.db.redisdb import check_user_ratelimit, get_redis_db
import pytest
from pydantic import BaseModel
from datetime import timedelta
import aioredis
from app.core.config import REDIS_IP, REDIS_PORT

@pytest.mark.asyncio
async def test_check_user_ratelimit_false():
    r = aioredis.from_url(f"redis://{REDIS_IP}:{REDIS_PORT}")

    class MockAuth0User(BaseModel):
        id: str

    # First request is not rate limited (user 111)
    is_ratelimited = await check_user_ratelimit(r, rate_limit_config=(1, timedelta(seconds=10)),user=MockAuth0User(id="111"))
    assert is_ratelimited == (MockAuth0User(id="111"), False)

    # Second request is rate limited (user 111)
    is_ratelimited = await check_user_ratelimit(r, rate_limit_config=(1, timedelta(seconds=10)),user=MockAuth0User(id="111"))
    assert is_ratelimited == (MockAuth0User(id="111"), True)

    # First request is not rate limited (user 222)
    is_ratelimited = await check_user_ratelimit(r, rate_limit_config=(1, timedelta(seconds=5)),user=MockAuth0User(id="222"))
    assert is_ratelimited == (MockAuth0User(id="222"), False)

    # close redis connection
    await r.close()