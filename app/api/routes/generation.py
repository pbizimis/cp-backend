from fastapi import APIRouter, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.api import GenerationOptions

router = APIRouter()

@router.post("/generate")
def generate_image(model: GenerationOptions, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model