import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from app.core.auth0 import auth
from app.db.mongodb import get_db
from app.main import get_app


@pytest.fixture
async def async_authenticated_app():

    authenticated_app = get_app()
    client = TestClient(authenticated_app)
    db = AsyncIOMotorClient("localhost", 27017)

    class MockAuth0User(BaseModel):
        id: str
        permission: list = None
        email: str = None

    def authenticated_user():
        return MockAuth0User(**{"id": "007"})

    def override_get_db():
        return db

    authenticated_app.dependency_overrides[auth.get_user] = authenticated_user
    authenticated_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=authenticated_app, base_url="http://localhost") as ac:
        yield ac, db
