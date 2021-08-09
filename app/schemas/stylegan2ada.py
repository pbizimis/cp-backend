from pydantic import BaseModel
from app.schemas.stylegan_models import stylegan2_ada_models, Model, StyleGanModel
from app.schemas.stylegan_methods import Slider, Dropdown, StyleGanMethod, SeedOrImage, Text
from app.stylegan.load_model import load_stylegan2ada_model_from_pkl
from app.stylegan.generation import generate_stylegan2ada_images
from app.stylegan.projection import run_projection
from app.stylegan.style_mixing import generate_style_mix
from typing import Union, Any

class StyleGan2ADA(StyleGanModel):
    
    folder_path = "stylegan2_ada_models/"
    loaded_models = {}

    def __init__(self, model: Model, method_options: dict) -> None:
        
        model.version = self.__class__.__name__
        self.model = self._load_model(model)
        self.method_options =  method_options
            
    def _check_for_loaded_models(self, model: Model) -> Union[bool, Any]:
        if model in self.loaded_models:
            return self.loaded_models[model]
        return False

    def _load_model(self, model: Model) -> Any:
        
        stylegan2ada_model = self._check_for_loaded_models(model)

        if stylegan2ada_model:
            return stylegan2ada_model
        
        stylegan2ada_model = load_stylegan2ada_model_from_pkl(self.folder_path, model)
        self.loaded_models[model] = stylegan2ada_model

        return stylegan2ada_model

    def generate(self) -> dict:
        return generate_stylegan2ada_images(self.model, self.method_options)


    def style_mix(self, row_image: Union[int, bytes], col_image: Union[int, bytes]) -> dict:
        return generate_style_mix(self.model, self.method_options, row_image, col_image)
        

class Generation(BaseModel):
    name: str = "Generation"
    model: Model
    truncation: float
    seed: str

class StyleMix(BaseModel):
    name: str = "StyleMix"
    model: Model
    row_image: str
    column_image: str
    styles: str
    truncation: float

generation_method = StyleGanMethod(
    name="Generate",
    description="Generate random images or from a certain seed.",
    method_options=(
        Dropdown(place=1, name="Model", options=stylegan2_ada_models.models, default=0, description="Choose your StyleGan2ADA model. The lower the FID value, the better the image quality."),
        Slider(place=2, name="Truncation", max=2, min=-2, step=0.1, default=1, description="Truncation controls how close the image is to the overall average image of the model. For example, a truncation value of 0 will always generate the same image, the average of all images that were used to train the model. The higher or lower the value, the more diverse will the image be. Be aware that an increase in image diversity means a loss in image quality. This happens because a high or low truncation value tells the model to generate an image far away from the average, which essentially is less data that the model can use to generate your image."),
        Text(place=3, name="Seed", default="", description="You can either choose an empty seed for a random generation, a specific seed value")
    )
)

stylemix_method = StyleGanMethod(
    name="StyleMix",
    description="Style mix two different images. The row image will adapt the styles of the column image.",
    method_options=(
        Dropdown(place=1, name="Model", options=stylegan2_ada_models.models, default=0, description="Choose your StyleGan2ADA model. The lower the FID value, the better the image quality."),
        SeedOrImage(name="Row_Image", place=2, default="", description="You can either choose an empty seed for a random generation, a specific seed value, or you can choose an image from your collection."),
        SeedOrImage(name="Column_Image", place=3, default="", description="You can either choose an empty seed for a random generation, a specific seed value, or you can choose an image from your collection."),
        Dropdown(place=4, name="Styles", options=("Coarse", "Middle", "Fine"), default=1, description="This dropdown allows to choose what kind of styles the row image adapts from the column image. Coarse styles are styles such as the content width (wide or narrow). Middle styles are structural styles such as grids, images, or text. Fine styles are almost only the color of the image."),
        Slider(place=5, name="Truncation", max=2, min=-2, step=0.1, default=1, description="If you decide to generate a seed, the truncation controls how close the image is to the overall average image of the model. For example, a truncation value of 0 will always generate the same image, the average of all images that were used to train the model. The higher or lower the value, the more diverse will the image be. Be aware that an increase in image diversity means a loss in image quality. This happens because a high or low truncation value tells the model to generate an image far away from the average, which essentially is less data that the model can use to generate your image."),
    )
)