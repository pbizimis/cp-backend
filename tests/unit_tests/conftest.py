import datetime

import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from app.core.auth0 import auth
from app.db.mongodb import get_mongodb
from app.db.redisdb import check_user_ratelimit
from app.main import get_app
from app.schemas.mongodb import ImageData
from app.schemas.stylegan_user import StyleGanUser
from app.stylegan.load_model import load_model_from_pkl_stylegan2ada

unauthenticated_app = get_app()
authenticated_app = get_app()
mongodb_stub = AsyncIOMotorClient()


@pytest.fixture(scope="session")
def G_model():
    """Return a loaded StyleGan2ADA model."""

    class MockModel(BaseModel):
        filename: str

    mock_model = MockModel(filename="img31res256fid12.pkl")

    model = load_model_from_pkl_stylegan2ada("stylegan2_ada_models", mock_model)

    return model


@pytest.fixture(scope="module")
def test_client():
    """Yield a test client that is not authenticated."""
    app = unauthenticated_app
    with TestClient(app) as client:
        yield client, app


@pytest.fixture(scope="module")
def test_authenticated_client():
    """Yield a test client that is authenticated."""
    app = authenticated_app
    with TestClient(app) as client:

        def override_get_mongodb():
            return mongodb_stub

        def override_check_user_ratelimit():
            return ("007", False)

        def override_auth0_user():
            return {"id": "007", "permissions": None, "email": None}

        class MockStyleGanUser:
            def __init__(
                self, user, db, stylegan_class=None, stylegan_method_options=None
            ):
                self.user = user
                self.db = db
                self.stylegan_class = stylegan_class
                self.stylegan_method_options = stylegan_method_options
                self.result = {}

            def style_mix_images(self):
                self.result = {
                    "result_image": "111111111111111",
                    "row_image": "2222222222222",
                    "col_image": "3333333333333",
                }

            def generate_image(self):
                self.result = {"result_image": "111111111111111"}

            async def save_user_images(self):
                return self.result

            async def get_user_images(self):
                return [
                    ImageData(
                        url="c31ad1323ed648feb93cd7398fcf1894",
                        auth0_id="google-oauth2|114778200891334419591",
                        creation_date=datetime.datetime(
                            2021, 7, 29, 14, 41, 57, 666000
                        ),
                        method={
                            "name": "StyleMix",
                            "model": {
                                "img": 31,
                                "res": 256,
                                "fid": 12,
                                "version": "StyleGan2ADA",
                            },
                            "row_image": "123",
                            "column_image": "123",
                            "styles": "Middle",
                            "truncation": 1.0,
                        },
                    ),
                    ImageData(
                        url="3bf5df238b3741559d9e3806c97f2d33",
                        auth0_id="google-oauth2|114778200891334419591",
                        creation_date=datetime.datetime(
                            2021, 7, 29, 14, 41, 57, 666000
                        ),
                        method={
                            "name": "StyleMix",
                            "model": {
                                "img": 31,
                                "res": 256,
                                "fid": 12,
                                "version": "StyleGan2ADA",
                            },
                            "row_image": "123",
                            "column_image": "123",
                            "styles": "Middle",
                            "truncation": 1.0,
                        },
                    ),
                ]

            async def delete_user_images(self, deletion_options):
                return True

            @classmethod
            def get_class(cls):
                return cls

        app.dependency_overrides[auth.get_user] = override_auth0_user
        app.dependency_overrides[check_user_ratelimit] = override_check_user_ratelimit
        app.dependency_overrides[StyleGanUser.get_class] = MockStyleGanUser.get_class
        app.dependency_overrides[get_mongodb] = override_get_mongodb

        yield client, app
