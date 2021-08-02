from app.schemas.stylegan_models import stylegan2_ada_models

url = "/api/v1/models"


def test_read_stylegan_models_unauthenticated(test_client):
    client, app = test_client

    resp = client.get(url)
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Missing bearer token"}


def test_read_stylegan_models_authenticated(test_authenticated_client):
    client, app = test_authenticated_client

    def override_stylegan2_ada_models():
        return [
            {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"},
            {"img": 20, "res": 512, "fid": 2, "version": "stylegan2"},
        ]

    app.dependency_overrides[stylegan2_ada_models] = override_stylegan2_ada_models

    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.json() == {
        "stylegan_models": {
            "version": "StyleGan2ADA",
            "models": [
                {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"},
                {"img": 20, "res": 512, "fid": 2, "version": "stylegan2"},
            ],
        }
    }
