from fastapi.testclient import TestClient


def test_config(test_client):
    client, app = test_client
    assert type(client.app.title) == str
    assert type(client.app.version) == str
    assert type(client.app.debug) == bool


def test_cors():
    pass


# def test_style_mix_images_authenticated_preflight_ok(test_authenticated_client):
# client, app = test_authenticated_client

# headers = {
#     "Origin": "https://webdesigan.com",
#     "Access-Control-Request-Method": "POST",
#     "Access-Control-Request-Headers": "authorization, content-type",
# }

# resp = client.options(stylemix_url, headers=headers)
# assert resp.status_code == 200
# assert resp.text == "OK"
