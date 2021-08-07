import json
import os

import PIL.Image
import requests

from app.core.config import API_PREFIX
from app.schemas.stylegan2ada import Generation, StyleMix
from app.schemas.stylegan_models import Model

# requires a running application instance on localhost:8000
# docker build . --tag api
# docker run -e MONGOPW=$MONGOPW -e AUTH0_DOMAIN=$AUTH0_DOMAIN -e AUTH0_API=$AUTH0_API -e GOOGLE_APPLICATION_CREDENTIALS=/app/testing_credentials.json -p 8000:80 api


def test_e2e():

    AUTH0_DOMAIN_ID = os.getenv("AUTH0_DOMAIN_ID")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
    GRANT_TYPE = "client_credentials"

    created_images = []

    # this applcation has access scope 'use:all'
    response = requests.post(
        "https://" + AUTH0_DOMAIN_ID + "/com/oauth/token",
        headers={"content-type": "application/json"},
        data=json.dumps(
            {
                "client_id": AUTH0_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "audience": AUTH0_AUDIENCE,
                "grant_type": GRANT_TYPE,
            }
        ),
    )

    access_token = response.json()["access_token"]

    BASE_URL = "http://localhost:8000" + API_PREFIX

    # not authenticated
    resp = requests.get(BASE_URL + "/models")
    assert resp.json() == {"detail": "Missing bearer token"}

    resp = requests.get(
        BASE_URL + "/models", headers={"Authorization": "Bearer " + access_token}
    )
    assert resp.json() == {
        "stylegan_models": [{
            "version": "StyleGan2ADA",
            "models": [{"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}],
        }]
    }

    resp = requests.get(
        BASE_URL + "/stylegan2ada/methods",
        headers={"Authorization": "Bearer " + access_token},
    )
    assert resp.json() == {
        "generation_method": {
            "name": "Generate",
            "description": "Generate random images or from a certain seed.",
            "method_options": [
                {
                    "type": "dropdown",
                    "name": "Model",
                    "place": 1,
                    "options": [
                        {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
                    ],
                    "default": 0,
                },
                {
                    "type": "slider",
                    "name": "Truncation",
                    "place": 2,
                    "max": 2,
                    "min": -2,
                    "step": 0.1,
                    "default": 1.0,
                },
                {"type": "text", "name": "Seed", "place": 3, "default": ""},
            ],
        },
        "stylemix_method": {
            "name": "StyleMix",
            "description": "Style mix different images.",
            "method_options": [
                {
                    "type": "dropdown",
                    "name": "Model",
                    "place": 1,
                    "options": [
                        {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
                    ],
                    "default": 0,
                },
                {
                    "type": "seed_or_image",
                    "name": "Row_Image",
                    "place": 2,
                    "default": "",
                },
                {
                    "type": "seed_or_image",
                    "name": "Column_Image",
                    "place": 3,
                    "default": "",
                },
                {
                    "type": "dropdown",
                    "name": "Styles",
                    "place": 4,
                    "options": ["Coarse", "Middle", "Fine"],
                    "default": 1,
                },
                {
                    "type": "slider",
                    "name": "Truncation",
                    "place": 5,
                    "max": 2,
                    "min": -2,
                    "step": 0.1,
                    "default": 1.0,
                },
            ],
        },
    }

    # Generation

    model = Model.from_filename("img31res256fid12.pkl", "stylegan2_ada_models/")

    resp = requests.post(
        BASE_URL + "/stylegan2ada/generate",
        headers={"Authorization": "Bearer " + access_token},
        json=Generation(model=model, truncation=1, seed="1234").dict(),
    )

    generated_image_id = resp.json()["result_image"]
    created_images.append(generated_image_id)
    url_prefix = resp.json()["url_prefix"]

    image = PIL.Image.open(
        requests.get(url_prefix + generated_image_id, stream=True).raw
    )

    assert image.size == (256, 256)

    resp = requests.post(
        BASE_URL + "/stylegan2ada/generate",
        headers={"Authorization": "Bearer " + access_token},
        json=Generation(model=model, truncation=1, seed="1234").dict(),
    )

    generated_image_id = resp.json()["result_image"]
    created_images.append(generated_image_id)
    url_prefix = resp.json()["url_prefix"]

    image = PIL.Image.open(
        requests.get(url_prefix + generated_image_id, stream=True).raw
    ).convert("RGB")

    # JPEG decoding can product small changes in image data and therefore, images cannot be compared by pixel data
    # Since this is an end2end test, images can be visually assessed if necessary
    # Image is at: print(url_prefix + generated_image_id)
    assert image.size == (256, 256)

    # Style Mix

    resp = requests.post(
        BASE_URL + "/stylegan2ada/stylemix",
        headers={"Authorization": "Bearer " + access_token},
        json=StyleMix(
            model=model,
            truncation=1,
            row_image="1234",
            column_image="5678",
            styles="Middle",
        ).dict(),
    )

    result_image_id = resp.json()["result_image"]
    row_image_id = resp.json()["row_image"]
    col_image_id = resp.json()["col_image"]
    created_images.extend([result_image_id, row_image_id, col_image_id])

    assert result_image_id is not None
    assert row_image_id is not None
    assert col_image_id is not None

    image = PIL.Image.open(
        requests.get(url_prefix + result_image_id, stream=True).raw
    ).convert("RGB")
    assert image.size == (256, 256)
    image = PIL.Image.open(
        requests.get(url_prefix + row_image_id, stream=True).raw
    ).convert("RGB")
    assert image.size == (256, 256)
    image = PIL.Image.open(
        requests.get(url_prefix + col_image_id, stream=True).raw
    ).convert("RGB")
    assert image.size == (256, 256)

    resp = requests.post(
        BASE_URL + "/stylegan2ada/stylemix",
        headers={"Authorization": "Bearer " + access_token},
        json=StyleMix(
            model=model,
            truncation=1,
            row_image=resp.json()["row_image"],
            column_image=resp.json()["col_image"],
            styles="Middle",
        ).dict(),
    )

    result_image_id = resp.json()["result_image"]
    row_image_id = resp.json()["row_image"]
    col_image_id = resp.json()["col_image"]
    created_images.extend([result_image_id, row_image_id, col_image_id])

    assert result_image_id is not None
    assert row_image_id is not None
    assert col_image_id is not None

    image = PIL.Image.open(
        requests.get(url_prefix + result_image_id, stream=True).raw
    ).convert("RGB")
    assert image.size == (256, 256)
    image = PIL.Image.open(
        requests.get(url_prefix + row_image_id, stream=True).raw
    ).convert("RGB")
    assert image.size == (256, 256)
    image = PIL.Image.open(
        requests.get(url_prefix + col_image_id, stream=True).raw
    ).convert("RGB")
    assert image.size == (256, 256)

    # GET IMAGES

    resp = requests.get(
        BASE_URL + "/user/images",
        headers={"Authorization": "Bearer " + access_token},
    )

    all_testing_images = resp.json()["image_ids"]
    all_testing_images_ids = []
    for image_dict in all_testing_images:
        all_testing_images_ids.append(image_dict["url"])

    # assert that all images created in this test have a database entry
    assert set(created_images).issubset(all_testing_images_ids)
