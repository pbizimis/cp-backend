from fastapi import APIRouter, Security
from fastapi_auth0 import Auth0User
from app.api.auth import auth

router = APIRouter()

@router.get("/random")
def generate_image():
    return {"message": "Generated!"}

@router.get("/protected")
def generate_image_protected(user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return {"message": "Protected Generated!"}