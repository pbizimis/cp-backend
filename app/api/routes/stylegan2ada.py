from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.stylegan2ada import StyleMix, Generation, generation_method, stylemix_method, StyleGan2ADA
from app.schemas.stylegan_user import StyleGanUser
from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import IMAGE_STORAGE_BASE_URL

router = APIRouter()

@router.post("/stylemix")
async def style_mix_images(stylemix_options: StyleMix, db: AsyncIOMotorClient = Depends(get_db),  user: Auth0User = Security(auth.get_user, scopes=["use:all"])):

    stylegan_user = StyleGanUser(user, stylemix_options, StyleGan2ADA, db)

    stylegan_user.stylemix_stylegan_images()

    image_id = await stylegan_user.save_stylegan_image()

    return {"image_url": IMAGE_STORAGE_BASE_URL + image_id}

@router.post("/generate")
async def generate_image(generation_options: Generation, db: AsyncIOMotorClient = Depends(get_db),  user: Auth0User = Security(auth.get_user, scopes=["use:all"])):

    stylegan_user = StyleGanUser(user, generation_options, StyleGan2ADA, db)

    stylegan_user.generate_stylegan_image()
    
    image_id = await stylegan_user.save_stylegan_image()

    return {"image_url": IMAGE_STORAGE_BASE_URL + image_id}

@router.get("/methods")
def generate_image(generation_method: dict = Depends(generation_method), stylemix_method: dict = Depends(stylemix_method), user: Auth0User = Security(auth.get_user, scopes=["use:all"])):
    return {
        "generation_method": generation_method,
        "stylemix_method": stylemix_method
        }
