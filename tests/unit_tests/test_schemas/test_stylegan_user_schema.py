from typing import Optional
from unittest.mock import call

import pytest
from fastapi_auth0 import Auth0User
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

import app
from app.schemas.mongodb import ImageData
from app.schemas.stylegan_models import Model, StyleGanModel
from app.schemas.stylegan_user import StyleGanUser, download_blob_from_gcs
from tests.unit_tests.conftest import db_stub


class MockStyleGanVersion(StyleGanModel):
    def __init__(self, model: Model, method_options: dict):
        model.version = self.__class__.__name__
        self.model = self._load_model(model)
        self.method_options = method_options

    def _load_model(self, model: Model):
        return "new model"

    def generate(self):
        return "generate image"

    def style_mix(self, row_image, column_image):
        return "stylemix " + row_image + " and " + column_image


class MockMethod(BaseModel):
    name: str = "Method"
    model: Optional[Model]
    row_image: Optional[str]
    column_image: Optional[str]
    styles: Optional[str]
    truncation: Optional[float]


mock_method = MockMethod(
    **{
        "model": Model(**{"img": 31, "res": 512, "fid": 12, "version": "version"}),
        "row_image": "1234",
        "column_image": "5678",
        "styles": "Middle",
        "truncation": 1.5,
    }
)

auth0_user = Auth0User(sub="007")


def test_styleganuser_init():

    # create StyleGanUser object without stylegan class or method
    stylegan_user = StyleGanUser(auth0_user, db_stub)
    assert stylegan_user.user == {"id": "007", "permissions": None, "email": None}
    assert type(stylegan_user.mongodb) == AsyncIOMotorClient
    assert stylegan_user.stylegan_class == None
    assert stylegan_user.stylegan_method_options == None

    # create StyleGanUser object with stylegan class and method
    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    assert stylegan_user.user == {"id": "007", "permissions": None, "email": None}
    assert type(stylegan_user.mongodb) == AsyncIOMotorClient
    assert stylegan_user.stylegan_class == MockStyleGanVersion
    assert stylegan_user.stylegan_method_options == mock_method
    # if stylegan class is given, an object is created
    assert type(stylegan_user.stylegan_model) == MockStyleGanVersion
    # can access loaded model from user object after init
    assert stylegan_user.stylegan_model.model == "new model"


def test_styleganuser_get_class():
    assert StyleGanUser.get_class() == StyleGanUser


def test_styleganuser_get_seed_or_image_vector(mocker):

    # return int if string is digits
    image_string = "1234"
    assert StyleGanUser.get_seed_or_image_vector(image_string) == int(1234)

    # call download_blob_from_gcs if string is not digits
    mocker.patch("app.schemas.stylegan_user.download_blob_from_gcs")
    image_string = "hexuid"
    StyleGanUser.get_seed_or_image_vector(image_string)
    app.schemas.stylegan_user.download_blob_from_gcs.assert_called_once_with(
        "stylegan-images-vectors", "hexuid"
    )


@pytest.mark.asyncio
async def test_get_user_images(mocker):
    mocker.patch("app.schemas.stylegan_user.get_user_images_from_mongodb")
    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    await stylegan_user.get_user_images()
    app.schemas.stylegan_user.get_user_images_from_mongodb.assert_called_once_with(
        db_stub, "007"
    )


def test_generate_image():

    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    stylegan_user.generate_image()
    assert stylegan_user.result_images_dict == "generate image"


def test_style_mix_images(mocker):
    def mock_get_seed_or_image_vector(value):
        return value

    mocker.patch(
        "app.schemas.stylegan_user.StyleGanUser.get_seed_or_image_vector",
        side_effect=mock_get_seed_or_image_vector,
    )

    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    stylegan_user.style_mix_images()
    assert stylegan_user.result_images_dict == "stylemix 1234 and 5678"


@pytest.mark.asyncio
async def test_save_user_images(mocker):
    def mock_upload_blob_to_gcs(*values):
        return "random_id_for_" + values[1]

    mocker.patch(
        "app.schemas.stylegan_user.upload_blob_to_gcs",
        side_effect=mock_upload_blob_to_gcs,
    )
    mocker.patch("app.schemas.stylegan_user.save_user_image_in_mongodb")

    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    stylegan_user.result_images_dict = {
        "result_image": ("result_image", "result_vector"),
        "row_image": ("seed_row_image", "w_row_blob"),
        "col_image": ("seed_col_image", "w_col_blob"),
    }
    result = await stylegan_user.save_user_images()
    assert result == {
        "result_image": "random_id_for_result_image",
        "row_image": "random_id_for_seed_row_image",
        "col_image": "random_id_for_seed_col_image",
    }

    # case if style mix is executed with row and col images that are already in db
    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    stylegan_user.result_images_dict = {
        "result_image": ("result_image", "result_vector"),
        "row_image": (None, None),
        "col_image": (None, None),
    }
    result = await stylegan_user.save_user_images()
    assert result == {
        "result_image": "random_id_for_result_image",
        "row_image": "1234",
        "col_image": "5678",
    }

    # case if style mix is executed with row image that is already in db
    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    stylegan_user.result_images_dict = {
        "result_image": ("result_image", "result_vector"),
        "row_image": (None, None),
        "col_image": ("seed_col_image", "w_col_blob"),
    }
    result = await stylegan_user.save_user_images()
    assert result == {
        "result_image": "random_id_for_result_image",
        "row_image": "1234",
        "col_image": "random_id_for_seed_col_image",
    }

    # case if style mix is executed with col image that is already in db
    stylegan_user = StyleGanUser(auth0_user, db_stub, MockStyleGanVersion, mock_method)
    stylegan_user.result_images_dict = {
        "result_image": ("result_image", "result_vector"),
        "row_image": ("seed_row_image", "w_row_blob"),
        "col_image": (None, None),
    }
    result = await stylegan_user.save_user_images()
    assert result == {
        "result_image": "random_id_for_result_image",
        "row_image": "random_id_for_seed_row_image",
        "col_image": "5678",
    }

    stylegan_user.result_images_dict = {
        "result_image": ("result_image", "result_vector")
    }
    result = await stylegan_user.save_user_images()
    assert result == {"result_image": "random_id_for_result_image"}
