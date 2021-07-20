from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.stylegan_models import stylegan2_ada_models

router = APIRouter()

@router.get("/models")
def read_stylegan_models(stylegan2ada_models: list = Depends(stylegan2_ada_models), user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return {"stylegan_models": {"version": "StyleGan2ADA", "models": stylegan2ada_models}}