from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User

from app.core.auth0 import auth
from app.schemas.stylegan_models import stylegan2ada_models

router = APIRouter()


@router.get("/models")
async def get_stylegan_models(
    stylegan2ada_models: list = Depends(stylegan2ada_models),
    user: Auth0User = Security(auth.get_user, scopes=["use:all"]),
) -> dict:
    """Get all supported stylegan models.

    Args:
        stylegan2ada_models (list, optional): a list of stylegan2ada models. Defaults to Depends(stylegan2ada_models).
        user (Auth0User, optional): the current user object (decoded JWT). Defaults to Security(auth.get_user, scopes=["use:all"]).

    Returns:
        dict: a dict with all stylegan versions and their models
    """
    return {
        "stylegan_models": [{"version": "StyleGan2ADA", "models": stylegan2ada_models}]
    }
