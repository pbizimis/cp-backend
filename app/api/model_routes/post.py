from fastapi import APIRouter, Security
from fastapi_auth0 import Auth0User
from app.api.auth import auth
from pydantic import BaseModel

router = APIRouter()

class Model(BaseModel):
    model: dict
    truncation: float

@router.post("/protected")
def generate_image_protected(model: Model, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model