import json
import os

import requests
from fastapi import FastAPI, Security
from fastapi.testclient import TestClient
from fastapi_auth0 import Auth0, Auth0User


def test_auth0_contract():

    # Test FASTAPI application that has the same auth0 schema as the main application

    app = FastAPI()

    auth = Auth0(
        domain="capstone-test.eu.auth0.com", api_audience="http://localhost:8000"
    )

    @app.get("/public")
    async def get_public():
        return {"message": "Anonymous user"}

    @app.get("/scure-no-scope")
    async def get_secure_no_scope(user: Auth0User = Security(auth.get_user)):
        return user

    @app.get("/scure-use-all")
    async def get_secure_scope_use_all(
        user: Auth0User = Security(auth.get_user, scopes=["use:all"])
    ):
        return user

    @app.get("/secure-use-other")
    async def get_secure_scope_use_all(
        user: Auth0User = Security(auth.get_user, scopes=["use:other"])
    ):
        return user

    client = TestClient(app)

    # get auth0 bearer token
    AUTH0_DOMAIN_ID = os.getenv("AUTH0_DOMAIN_ID")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
    GRANT_TYPE = "client_credentials"

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

    resp = client.get(
        "/scure-no-scope", headers={"Authorization": "Bearer " + access_token}
    )
    assert resp.status_code == 200
    assert "sub" in resp.json()
    assert "permissions" in resp.json()

    resp = client.get(
        "/scure-use-all", headers={"Authorization": "Bearer " + access_token}
    )
    assert resp.status_code == 200
    assert "sub" in resp.json()
    assert "permissions" in resp.json()

    resp = client.get(
        "/secure-use-other", headers={"Authorization": "Bearer " + access_token}
    )
    assert resp.status_code == 403
    assert resp.json() == {"detail": 'Missing "use:other" scope'}
