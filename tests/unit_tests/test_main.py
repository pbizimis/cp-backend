from fastapi.testclient import TestClient


def test_config(test_client):
    """Unit test app creation config."""
    client, app = test_client
    assert type(client.app.title) == str
    assert type(client.app.version) == str
    assert type(client.app.debug) == bool


def test_cors(test_authenticated_client):
    """Unit test preflight CORS response."""
    client, app = test_authenticated_client

    headers = {
        "Origin": "https://webdesigan.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization, content-type",
    }

    resp = client.options("/console/stylegan2ada", headers=headers)
    assert resp.status_code == 200
    assert resp.text == "OK"
    assert (
    resp.headers["access-control-allow-origin"]
    == "https://webdesigan.com"
    )
    assert resp.headers["access-control-allow-headers"] == "authorization, content-type"
