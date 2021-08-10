import aioredis
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from app.core.auth0 import auth
from app.db.mongodb import mongodb
from app.db.redisdb import redisdb
from app.main import get_app
from app.schemas.mongodb import MongoClient


class MockAuth0User(BaseModel):
    id: str
    permission: list = None
    email: str = None


@pytest.fixture
async def async_authenticated_app():
    """Pytest fixture for an async authenticated test client."""

    authenticated_app = get_app()
    client = TestClient(authenticated_app)
    mongodb_test = MongoClient()
    mongodb_test.client = AsyncIOMotorClient("localhost", 27017)
    redisdb.client = aioredis.from_url(f"redis://localhost:6379")

    def authenticated_user():
        return MockAuth0User(**{"id": "007"})

    authenticated_app.dependency_overrides[auth.get_user] = authenticated_user
    authenticated_app.dependency_overrides[mongodb.get_client] = mongodb_test.get_client

    async with AsyncClient(app=authenticated_app, base_url="http://localhost") as ac:
        yield ac, mongodb_test, authenticated_app
