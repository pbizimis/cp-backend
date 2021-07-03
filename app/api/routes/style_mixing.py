from fastapi import APIRouter, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from pydantic import BaseModel

router = APIRouter()

class StyleMixOptions(BaseModel):
    model: str
    images: list

@router.post("/stylemix")
def style_mix_images(model: StyleMixOptions, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model