from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.stylegan2ada import StyleMix, Generation, generation_method, stylemix_method
from app.schemas.stylegan_models import stylegan2_ada_models

router = APIRouter()

@router.get("/models")
def read_stylegan_models(models: list = Depends(stylegan2_ada_models)):
    return {"message": models}

@router.post("/stylemix")
def style_mix_images(model: StyleMix, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model

@router.post("/generate")
def generate_image(model: Generation, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model

@router.get("/methods")
def generate_image(generation_method: dict = Depends(generation_method), stylemix_method: dict = Depends(stylemix_method), user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return {
        "generation_method": generation_method,
        "stylemix_method": stylemix_method
        }
