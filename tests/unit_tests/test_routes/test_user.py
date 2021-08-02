from app.schemas.stylegan_models import stylegan2_ada_models
from app.schemas.stylegan2ada import generation_method, stylemix_method
import datetime
from app.schemas.mongodb import Image

user_url = "/api/v1/user/images"


def test_user_images_unauthenticated(test_client):
    """Wrong http method"""
    client, app = test_client

    resp = client.get(user_url)
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Missing bearer token"}


def test_style_mix_images_authenticated_right_payload(test_authenticated_client):
    client, app = test_authenticated_client

    resp = client.get(user_url)
    assert resp.status_code == 200
    assert resp.json() == {
        "image_url_prefix": "https://images.webdesigan.com/",
        "image_ids": [
            {
                "url": "c31ad1323ed648feb93cd7398fcf1894",
                "auth0_id": "google-oauth2|114778200891334419591",
                "creation_date": "2021-07-29T14:41:57.666000",
                "method": {
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
            },
            {
                "url": "3bf5df238b3741559d9e3806c97f2d33",
                "auth0_id": "google-oauth2|114778200891334419591",
                "creation_date": "2021-07-29T14:41:57.666000",
                "method": {
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
            },
        ],
    }
