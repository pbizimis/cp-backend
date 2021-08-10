import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from app.core.auth0 import auth
from app.db.mongodb import get_mongodb
from app.main import get_app


class MockAuth0User(BaseModel):
    id: str
    permission: list = None
    email: str = None


@pytest.fixture
async def async_authenticated_app():
    """Pytest fixture for an async authenticated test client."""

    authenticated_app = get_app()
    client = TestClient(authenticated_app)
    mongodb = AsyncIOMotorClient("localhost", 27017)

    # Mock functions
    def override_get_mongodb():
        return mongodb

    def authenticated_user():
        return MockAuth0User(**{"id": "007"})

    authenticated_app.dependency_overrides[auth.get_user] = authenticated_user
    authenticated_app.dependency_overrides[get_mongodb] = override_get_mongodb

    async with AsyncClient(app=authenticated_app, base_url="http://localhost") as ac:
        yield ac, mongodb, authenticated_app
