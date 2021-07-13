from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.api import StyleMixOptions, GenerationOptions
from app.schemas.stylegan_models import stylegan2_ada_models

router = APIRouter()

@router.get("/models")
def read_stylegan_models(models: list = Depends(stylegan2_ada_models)):
    return {"message": models}

@router.post("/stylemix")
def style_mix_images(model: StyleMixOptions, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model

@router.post("/generate")
def generate_image(model: GenerationOptions, user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return model

@router.get("/generate")
def generate_image(schema: dict = Depends(GenerationOptions.get_schema)):
    return {"form_fields": schema["properties"]}
