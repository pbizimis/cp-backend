from fastapi_auth0 import Auth0User
from app.schemas.stylegan_models import StyleGanModel
from typing import Type
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.mongodb import save_image, delete_image
from app.schemas.mongodb import Image
from app.db.google_cloud_storage import upload_blob

class StyleGanUser:

    def __init__(self, user: Auth0User, stylegan_method_options: dict, stylegan_class: Type[StyleGanModel], db: AsyncIOMotorClient):
        self.user = user
        self.stylegan_method_options = stylegan_method_options
        self.stylegan_class = stylegan_class
        self.db = db
        self.stylegan_model = self._load_stylegan_model()

    def _load_stylegan_model(self) -> StyleGanModel:
        return self.stylegan_class(self.stylegan_method_options.model, self.stylegan_method_options)

    def generate_stylegan_image(self) -> None:
        self.image_blob = self.stylegan_model.generate()
    
    async def save_stylegan_image(self) -> None:
        self.image_id = upload_blob("stylegan-images", self.image_blob)
        image_data = Image(url=self.image_id, auth0_id=self.user.id, stylegan_data=self.stylegan_method_options)
        await save_image(self.db, self.user.id, image_data)