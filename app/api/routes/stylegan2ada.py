from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User
from app.core.auth0 import auth
from app.schemas.stylegan2ada import StyleMix, Generation, generation_method, stylemix_method, StyleGan2ADA
from app.schemas.stylegan_user import StyleGanUser
from app.db.mongodb import get_db
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import IMAGE_STORAGE_BASE_URL
from app.db.redisdb import check_user_ratelimit
from aioredis import Redis

router = APIRouter()

@router.post("/stylemix")
async def style_mix_images(stylemix_options: StyleMix, db: AsyncIOMotorClient = Depends(get_db), ratelimited_user: tuple = Depends(check_user_ratelimit), stylegan_user_class = Depends(StyleGanUser.get_class)) -> dict:

    user = ratelimited_user[0]
    is_ratelimited = ratelimited_user[1]
    if is_ratelimited:
        return {"message": "You are rate limited!"}

    stylegan_user = stylegan_user_class(user, db, StyleGan2ADA, stylemix_options)

    stylegan_user.stylemix_stylegan_images()

    image_ids = await stylegan_user.save_stylegan_image()
    image_ids["url_prefix"] = IMAGE_STORAGE_BASE_URL
    return image_ids

@router.post("/generate")
async def generate_image(generation_options: Generation, db: AsyncIOMotorClient = Depends(get_db), ratelimited_user: tuple = Depends(check_user_ratelimit), stylegan_user_class = Depends(StyleGanUser.get_class)) -> dict:

    user = ratelimited_user[0]
    is_ratelimited = ratelimited_user[1]
    if is_ratelimited:
        return {"message": "You are rate limited!"}
        
    stylegan_user = stylegan_user_class(user, db, StyleGan2ADA, generation_options)

    stylegan_user.generate_stylegan_image()
    
    image_id = await stylegan_user.save_stylegan_image()
    image_id["url_prefix"] = IMAGE_STORAGE_BASE_URL

    return image_id

@router.get("/methods")
async def get_stylegan2ada_methods(generation_method: dict = Depends(generation_method), stylemix_method: dict = Depends(stylemix_method), user: Auth0User = Security(auth.get_user, scopes=["use:all"])) -> dict:
    return {
        "generation_method": generation_method,
        "stylemix_method": stylemix_method
        }
