import json
import os
import uuid
from datetime import datetime

import pytest
from pydantic import BaseModel

from app.core.config import IMAGE_STORAGE_BASE_URL
from app.db.mongodb import delete_all_images
from app.schemas.stylegan2ada import Generation, StyleMix
from app.schemas.stylegan_methods import StyleGanMethod
from app.schemas.stylegan_models import Model
from tests.integration_tests.narrow.assertion_dict import assertion_user_result


@pytest.mark.asyncio
async def test_style_mix_images_authenticated(async_authenticated_app, mocker):
    app, db = async_authenticated_app

    def override_upload_blob(bucket_name, image, image_id: str = None):
        if not image_id:
            image_id = "this_is_hex_uid"
        return image_id

    # prevent upload and download from gcs
    mocker.patch(
        "app.schemas.stylegan_user.upload_blob", side_effect=override_upload_blob
    )
    mocker.patch("app.schemas.stylegan_user.download_blob")

    # freeze time

    class Image(BaseModel):
        url: str
        auth0_id: str
        creation_date: datetime = datetime(2020, 2, 2, 20, 20, 20)
        method: dict

    def return_image(url, auth0_id, method):
        return Image(url=url, auth0_id=auth0_id, method=method)

    mocker.patch("app.schemas.stylegan_user.Image", side_effect=return_image)

    # at this point there are only stylegan2ada models
    stylegan2ada_models = os.listdir("stylegan2_ada_models/")
    stylegan2ada_models = [
        Model.from_filename(x, "stylegan2_ada_models/") for x in stylegan2ada_models
    ]

    assertion_resp = {
        "stylegan_models": [{"version": "StyleGan2ADA", "models": stylegan2ada_models}]
    }

    resp = await app.get("/api/v1/models")
    assert resp.status_code == 200
    assert resp.json() == assertion_resp

    resp = await app.get("/api/v1/stylegan2ada/methods")

    assert resp.status_code == 200
    for value in resp.json().values():
        try:
            assert StyleGanMethod(**value)
        except:
            pytest.fail(value, "needs to be of type StyleGanMethod!")

    # GENERATION

    generation_model = stylegan2ada_models[0]

    # seed defined
    resp = await app.post(
        "/api/v1/stylegan2ada/generate",
        json=Generation(model=generation_model, truncation=1, seed="1234").dict(),
    )
    image_id = resp.json()["result_image"]
    url_prefix = resp.json()["url_prefix"]
    assert image_id == "this_is_hex_uid"
    assert url_prefix == IMAGE_STORAGE_BASE_URL

    # seed empty (random)
    resp = await app.post(
        "/api/v1/stylegan2ada/generate",
        json=Generation(model=generation_model, truncation=1, seed="").dict(),
    )
    image_id = resp.json()["result_image"]
    url_prefix = resp.json()["url_prefix"]
    assert image_id == "this_is_hex_uid"
    assert url_prefix == IMAGE_STORAGE_BASE_URL

    # STYLE MIX

    stylemix_model = stylegan2ada_models[0]

    # stylemix two seeds
    resp = await app.post(
        "/api/v1/stylegan2ada/stylemix",
        json=StyleMix(
            model=stylemix_model,
            truncation=1,
            row_image="1234",
            column_image="5678",
            styles="Fine",
        ).dict(),
    )
    mixed_image_id = resp.json()["result_image"]
    row_image_id = resp.json()["row_image"]
    col_image_id = resp.json()["col_image"]
    url_prefix = resp.json()["url_prefix"]
    assert image_id == "this_is_hex_uid"
    assert row_image_id == "this_is_hex_uid"
    assert col_image_id == "this_is_hex_uid"
    assert url_prefix == IMAGE_STORAGE_BASE_URL

    def override_download_blob(bucket_name, image_id):
        with open(
            "tests/unit_tests/test_stylegan/assertion_files/save_vector_as_bytes_assertion_result.txt",
            "rb",
        ) as f:
            w_bytes_value = f.read()
        return w_bytes_value

    mocker.patch(
        "app.schemas.stylegan_user.download_blob", side_effect=override_download_blob
    )

    # stylemix seed and already existing image (row, col)
    resp = await app.post(
        "/api/v1/stylegan2ada/stylemix",
        json=StyleMix(
            model=stylemix_model,
            truncation=1,
            row_image="1234",
            column_image="image_id",
            styles="Middle",
        ).dict(),
    )
    mixed_image_id = resp.json()["result_image"]
    row_image_id = resp.json()["row_image"]
    col_image_id = resp.json()["col_image"]
    url_prefix = resp.json()["url_prefix"]
    assert image_id == "this_is_hex_uid"
    assert row_image_id == "this_is_hex_uid"
    assert col_image_id == "image_id"
    assert url_prefix == IMAGE_STORAGE_BASE_URL

    # stylemix seed and already existing image (col, row)
    resp = await app.post(
        "/api/v1/stylegan2ada/stylemix",
        json=StyleMix(
            model=stylemix_model,
            truncation=1,
            row_image="image_id",
            column_image="1234",
            styles="Coarse",
        ).dict(),
    )
    mixed_image_id = resp.json()["result_image"]
    row_image_id = resp.json()["row_image"]
    col_image_id = resp.json()["col_image"]
    url_prefix = resp.json()["url_prefix"]
    assert image_id == "this_is_hex_uid"
    assert col_image_id == "this_is_hex_uid"
    assert row_image_id == "image_id"
    assert url_prefix == IMAGE_STORAGE_BASE_URL

    # stylemix two already existing images
    resp = await app.post(
        "/api/v1/stylegan2ada/stylemix",
        json=StyleMix(
            model=stylemix_model,
            truncation=1,
            row_image="image_id_1",
            column_image="image_id_2",
            styles="Coarse",
        ).dict(),
    )
    mixed_image_id = resp.json()["result_image"]
    row_image_id = resp.json()["row_image"]
    col_image_id = resp.json()["col_image"]
    url_prefix = resp.json()["url_prefix"]
    assert image_id == "this_is_hex_uid"
    assert row_image_id == "image_id_1"
    assert col_image_id == "image_id_2"
    assert url_prefix == IMAGE_STORAGE_BASE_URL

    # USER

    resp = await app.get("/api/v1/user/images")
    all_user_images = json.loads(resp.text)
    assert all_user_images == assertion_user_result

    # DELETE (CLEANUP)

    await delete_all_images(db, auth0_id="007")

    # The asnyc http library used for this integration test does not support bodies on http DELETE requests.
    # Usually the DELETE methods can have a request body as specified in https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/DELETE
    # Therefore, DELETE tests are continued in the end2end test as well as unit tests