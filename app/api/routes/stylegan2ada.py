from aioredis import Redis
from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.auth0 import auth
from app.core.config import IMAGE_STORAGE_BASE_URL
from app.db.mongodb import get_mongodb
from app.db.redisdb import check_user_ratelimit
from app.schemas.stylegan2ada import (
    Generation,
    StyleGan2ADA,
    StyleMix,
    generation_method,
    stylemix_method,
)
from app.schemas.stylegan_user import StyleGanUser

router = APIRouter()


@router.post("/stylemix")
async def style_mix_images_stylegan2ada(
    style_mix_options: StyleMix,
    mongodb: AsyncIOMotorClient = Depends(get_mongodb),
    ratelimited_user: tuple = Depends(check_user_ratelimit),
    stylegan_user_class=Depends(StyleGanUser.get_class),
) -> dict:

    user = ratelimited_user[0]
    is_ratelimited = ratelimited_user[1]
    if is_ratelimited:
        return {"message": "You are rate limited!"}

    stylegan_user = stylegan_user_class(user, mongodb, StyleGan2ADA, style_mix_options)

    stylegan_user.style_mix_images()

    image_ids = await stylegan_user.save_user_images()
    image_ids["url_prefix"] = IMAGE_STORAGE_BASE_URL
    return image_ids


@router.post("/generate")
async def generate_image_stylegan2ada(
    generation_options: Generation,
    mongodb: AsyncIOMotorClient = Depends(get_mongodb),
    ratelimited_user: tuple = Depends(check_user_ratelimit),
    stylegan_user_class=Depends(StyleGanUser.get_class),
) -> dict:

    user = ratelimited_user[0]
    is_ratelimited = ratelimited_user[1]
    if is_ratelimited:
        return {"message": "You are rate limited!"}

    stylegan_user = stylegan_user_class(user, mongodb, StyleGan2ADA, generation_options)

    stylegan_user.generate_image()

    image_id = await stylegan_user.save_user_images()
    image_id["url_prefix"] = IMAGE_STORAGE_BASE_URL

    return image_id


@router.get("/methods")
async def get_methods_stylegan2ada(
    generation_method: dict = Depends(generation_method),
    stylemix_method: dict = Depends(stylemix_method),
    user: Auth0User = Security(auth.get_user, scopes=["use:all"]),
) -> dict:
    return {"generation_method": generation_method, "stylemix_method": stylemix_method}
