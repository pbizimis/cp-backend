from fastapi import APIRouter, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from pydantic import BaseModel

router = APIRouter()

class GenerationOptions(BaseModel):
    model: str
    truncation: float

@router.post("/generate")
def generate_image(model: GenerationOptions, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model