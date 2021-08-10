import json

from app.db.redisdb import check_user_ratelimit
from app.schemas.stylegan2ada import generation_method, stylemix_method
from app.schemas.stylegan_models import stylegan2ada_models

# STYLE MIX
stylemix_url = "/api/v1/stylegan2ada/stylemix"


def test_style_mix_images_stylegan2ada_unauthenticated(test_client):
    """Unit test unauthenticated request."""
    client, app = test_client

    resp = client.post(stylemix_url)
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Missing bearer token"}


def test_style_mix_images_stylegan2ada_authenticated_wrong_payload(
    test_authenticated_client,
):
    """Unit test an authenticated request with wrong payload."""
    client, app = test_authenticated_client

    # Payload is missing
    resp = client.post(stylemix_url)
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {"loc": ["body"], "msg": "field required", "type": "value_error.missing"}
        ]
    }

    # Payload is broken json
    resp = client.post(
        stylemix_url, headers={"content-type": "application/json"}, data="{broken json}"
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "loc": ["body", 1],
                "msg": "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
                "type": "value_error.jsondecode",
                "ctx": {
                    "msg": "Expecting property name enclosed in double quotes",
                    "doc": "{broken json}",
                    "pos": 1,
                    "lineno": 1,
                    "colno": 2,
                },
            }
        ]
    }

    # Payload is the wrong data type
    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"row_image":"123","column_image":"456","styles":"Middle","truncation":"string"}'
    resp = client.post(
        stylemix_url, headers={"Content-Type": "application/json"}, data=data
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "loc": ["body", "truncation"],
                "msg": "value is not a valid float",
                "type": "type_error.float",
            }
        ]
    }


def test_style_mix_images_stylegan2ada_authenticated_wrong_headers(
    test_authenticated_client,
):
    """Unit test an authenticated request with wrong header."""
    client, app = test_authenticated_client

    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"row_image":"123","column_image":"456","styles":"Middle","truncation":1}'
    resp = client.post(stylemix_url, headers={"Content-Type": "text/plain"}, data=data)
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "loc": ["body"],
                "msg": "value is not a valid dict",
                "type": "type_error.dict",
            }
        ]
    }


def test_style_mix_images_stylegan2ada_authenticated_ratelimited(
    test_authenticated_client,
):
    """Unit test a ratelimited request."""
    client, app = test_authenticated_client

    # Activate rate limit
    def override_check_user_ratelimit():
        return ("007", True)

    app.dependency_overrides[check_user_ratelimit] = override_check_user_ratelimit

    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"row_image":"123","column_image":"456","styles":"Middle","truncation":1}'
    resp = client.post(
        stylemix_url, headers={"Content-Type": "application/json"}, data=data
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "You are rate limited!"}

    # Deactivate rate limit
    def override_check_user_ratelimit():
        return ("007", False)

    app.dependency_overrides[check_user_ratelimit] = override_check_user_ratelimit


def test_style_mix_images_stylegan2ada_authenticated_right_payload(
    test_authenticated_client,
):
    """Unit test an authenticated request with right payload."""
    client, app = test_authenticated_client

    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"row_image":"123","column_image":"456","styles":"Middle","truncation":1}'
    resp = client.post(
        stylemix_url, headers={"Content-Type": "application/json"}, data=data
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "result_image": "111111111111111",
        "row_image": "2222222222222",
        "col_image": "3333333333333",
        "url_prefix": "https://images.webdesigan.com/",
    }


# Generation
generation_url = "/api/v1/stylegan2ada/generate"


def test_generate_image_stylegan2ada_unauthenticated(test_client):
    """Unit test unauthenticated request."""
    client, app = test_client

    resp = client.post(generation_url)
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Missing bearer token"}


def test_generate_image_stylegan2ada_authenticated_wrong_payload(
    test_authenticated_client,
):
    """Unit test an authenticated request with wrong payload."""
    client, app = test_authenticated_client

    # Payload is missing
    resp = client.post(generation_url)
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {"loc": ["body"], "msg": "field required", "type": "value_error.missing"}
        ]
    }

    # Payload is broken json
    resp = client.post(
        stylemix_url, headers={"content-type": "application/json"}, data="{broken json}"
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "loc": ["body", 1],
                "msg": "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
                "type": "value_error.jsondecode",
                "ctx": {
                    "msg": "Expecting property name enclosed in double quotes",
                    "doc": "{broken json}",
                    "pos": 1,
                    "lineno": 1,
                    "colno": 2,
                },
            }
        ]
    }

    # Payload is the wrong data type
    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"truncation":"string","seed":123456}'
    resp = client.post(
        generation_url, headers={"Content-Type": "application/json"}, data=data
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "loc": ["body", "truncation"],
                "msg": "value is not a valid float",
                "type": "type_error.float",
            }
        ]
    }


def test_generate_image_stylegan2ada_authenticated_wrong_headers(
    test_authenticated_client,
):
    """Unit test an authenticated request with wrong header."""
    client, app = test_authenticated_client

    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"truncation":1.2,"seed":123456}'
    resp = client.post(
        generation_url, headers={"Content-Type": "text/plain"}, data=data
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "loc": ["body"],
                "msg": "value is not a valid dict",
                "type": "type_error.dict",
            }
        ]
    }


def test_generate_image_stylegan2ada_authenticated_ratelimited(
    test_authenticated_client,
):
    """Unit test a ratelimited request."""
    client, app = test_authenticated_client

    # Activate rate limit
    def override_check_user_ratelimit():
        return ("007", True)

    app.dependency_overrides[check_user_ratelimit] = override_check_user_ratelimit

    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"row_image":"123","column_image":"456","styles":"Middle","truncation":1}'
    resp = client.post(
        stylemix_url, headers={"Content-Type": "application/json"}, data=data
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "You are rate limited!"}

    # Deactivate rate limit
    def override_check_user_ratelimit():
        return ("007", False)

    app.dependency_overrides[check_user_ratelimit] = override_check_user_ratelimit


def test_generate_image_stylegan2ada_authenticated_right_payload(
    test_authenticated_client,
):
    """Unit test an authenticated request with right payload."""
    client, app = test_authenticated_client

    data = '{"model":{"img":31,"res":256,"fid":12,"version":"stylegan2_ada"},"truncation":1.2,"seed":123456}'
    resp = client.post(
        generation_url, headers={"Content-Type": "application/json"}, data=data
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "result_image": "111111111111111",
        "url_prefix": "https://images.webdesigan.com/",
    }


# Methods
methods_url = "/api/v1/stylegan2ada/methods"


def test_get_stylegan2ada_methods_unauthenticated(test_client):
    """Unit test unauthenticated request."""
    client, app = test_client

    resp = client.get(methods_url)
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Missing bearer token"}


def test_get_stylegan2ada_methods_authenticated(test_authenticated_client):
    """Unit test an authenticated request."""
    client, app = test_authenticated_client

    generation_method_json = "{'name': 'Generate', 'description': 'Generate random images or from a certain seed.', 'method_options': (Dropdown(type='dropdown', name='Model', place=1, options=(Model(img=31, res=256, fid=12, version='stylegan2_ada'),), default=0), Slider(type='slider', name='Truncation', place=2, max=2, min=-2, step=0.1, default=1.0), Text(type='text', name='Seed', place=3, default=''))}"
    stylemix_method_json = "{'name': 'StyleMix', 'description': 'Style mix different images.', 'method_options': (Dropdown(type='dropdown', name='Model', place=1, options=(Model(img=31, res=256, fid=12, version='stylegan2_ada'),), default=0), SeedOrImage(type='seed_or_image', name='Row_Image', place=2, default=''), SeedOrImage(type='seed_or_image', name='Column_Image', place=3, default=''), Dropdown(type='dropdown', name='Styles', place=4, options=('Coarse', 'Middle', 'Fine'), default=1), Slider(type='slider', name='Truncation', place=5, max=2, min=-2, step=0.1, default=1.0))}"

    def override_generation_method():
        return generation_method_json

    def override_stylemix_method():
        return stylemix_method_json

    app.dependency_overrides[generation_method] = override_generation_method
    app.dependency_overrides[stylemix_method] = override_stylemix_method

    resp = client.get(methods_url)
    assert resp.status_code == 200
    assert resp.json() == {
        "generation_method": generation_method_json,
        "stylemix_method": stylemix_method_json,
    }
