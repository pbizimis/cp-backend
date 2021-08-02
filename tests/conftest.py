from fastapi.testclient import TestClient
from app.main import get_app
import pytest
from app.core.auth0 import auth
from app.schemas.stylegan_user import StyleGanUser
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.mongodb import get_db
import datetime
from app.schemas.mongodb import Image
from app.stylegan.load_model import load_stylegan2ada_model_from_pkl
from pydantic import BaseModel

unauthenticated_app = get_app()
authenticated_app = get_app()
db_stub = AsyncIOMotorClient()

@pytest.fixture(scope="session")
def G_model():
    class MockModel(BaseModel):
        filename: str

    mock_model = MockModel(filename="img31res256fid12.pkl")

    model = load_stylegan2ada_model_from_pkl("stylegan2_ada_models", mock_model)

    return model


@pytest.fixture(scope="module")
def test_client():
    app = unauthenticated_app
    with TestClient(app) as client:
        yield client, app


@pytest.fixture(scope="module")
def test_authenticated_client():
    app = authenticated_app
    with TestClient(app) as client:

        def authenticated_user():
            return {"id": "007", "permissions": None, "email": None}

        class OverrideStyleGanUser:
            def __init__(
                self, user, db, stylegan_class=None, stylegan_method_options=None
            ):
                self.user = user
                self.db = db
                self.stylegan_class = stylegan_class
                self.stylegan_method_options = stylegan_method_options
                self.result = {}

            def stylemix_stylegan_images(self):
                self.result = {
                    "result_image": "111111111111111",
                    "row_image": "2222222222222",
                    "col_image": "3333333333333",
                }

            def generate_stylegan_image(self):
                self.result = {"result_image": "111111111111111"}

            async def save_stylegan_image(self):
                return self.result

            async def get_images(self):
                return [
                    Image(
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
                    Image(
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

            @classmethod
            def get_class(cls):
                return cls

        def override_get_db():
            return db_stub

        app.dependency_overrides[auth.get_user] = authenticated_user
        app.dependency_overrides[
            StyleGanUser.get_class
        ] = OverrideStyleGanUser.get_class
        app.dependency_overrides[get_db] = override_get_db

        yield client, app