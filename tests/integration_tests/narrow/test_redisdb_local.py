from datetime import timedelta

import aioredis
import pytest
from pydantic import BaseModel

from app.core.config import REDIS_URL
from app.db.redisdb import check_user_ratelimit, redisdb


@pytest.mark.asyncio
async def test_redisdb():
    """Test application logic against a local instance of Redis."""
    redis_client = aioredis.from_url(REDIS_URL)

    class MockAuth0User(BaseModel):
        id: str

    # First request is not rate limited (user 111)
    is_ratelimited = await check_user_ratelimit(
        redis_client,
        redis_ratelimit_config=(1, timedelta(seconds=10)),
        user=MockAuth0User(id="111"),
    )
    assert is_ratelimited == (MockAuth0User(id="111"), False)

    # Second request is rate limited (user 111)
    is_ratelimited = await check_user_ratelimit(
        redis_client,
        redis_ratelimit_config=(1, timedelta(seconds=10)),
        user=MockAuth0User(id="111"),
    )
    assert is_ratelimited == (MockAuth0User(id="111"), True)

    # First request is not rate limited (user 222)
    is_ratelimited = await check_user_ratelimit(
        redis_client,
        redis_ratelimit_config=(1, timedelta(seconds=5)),
        user=MockAuth0User(id="222"),
    )
    assert is_ratelimited == (MockAuth0User(id="222"), False)

    await redis_client.close()
