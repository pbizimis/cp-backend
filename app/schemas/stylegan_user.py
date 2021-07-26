from fastapi_auth0 import Auth0User
from app.schemas.stylegan_models import StyleGanModel
from typing import Type
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.mongodb import save_image, delete_image, get_user_images
from app.schemas.mongodb import Image
from app.db.google_cloud_storage import upload_blob, download_blob

class StyleGanUser:

    def __init__(self, user: Auth0User, db: AsyncIOMotorClient, stylegan_class: Type[StyleGanModel] = None, stylegan_method_options: dict = None):
        self.user = user
        self.stylegan_method_options = stylegan_method_options
        self.stylegan_class = stylegan_class
        self.db = db
        if self.stylegan_class:
            self.stylegan_model = self._load_stylegan_model()

    def _load_stylegan_model(self) -> StyleGanModel:
        return self.stylegan_class(self.stylegan_method_options.model, self.stylegan_method_options)

    async def get_images(self) -> list:
        return await get_user_images(self.db, self.user.id)

    def generate_stylegan_image(self) -> None:
        self.blobs = self.stylegan_model.generate()

    def stylemix_stylegan_images(self) -> None:
        row_image = self.get_seed_or_image_vector(self.stylegan_method_options.row_image)
        column_image = self.get_seed_or_image_vector(self.stylegan_method_options.column_image)

        self.blobs = self.stylegan_model.style_mix(row_image, column_image)
    
    async def save_stylegan_image(self) -> str:
        for key, blobs in self.blobs.items():
            image_blob, w_blob = blobs
            if not (image_blob and w_blob):
                self.blobs[key] = self.stylegan_method_options.row_image if key == "row_image" else self.stylegan_method_options.column_image
                continue
            image_id = upload_blob("stylegan-images", image_blob)
            upload_blob("stylegan-images-vectors", w_blob, image_id)
            image_data = Image(url=image_id, auth0_id=self.user.id, method=self.stylegan_method_options)
            await save_image(self.db, self.user.id, image_data)
            self.blobs[key] = image_id
        return self.blobs

    @staticmethod
    def get_seed_or_image_vector(image_string):
        if image_string.isdigit():
            return int(image_string)
        else:
            return download_blob("stylegan-images-vectors", image_string)