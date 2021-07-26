from pydantic import BaseModel
from app.schemas.stylegan_models import stylegan2_ada_models, Model, StyleGanModel
from app.schemas.stylegan_methods import Slider, Dropdown, StyleGanMethod, SeedOrImage, Text
from app.stylegan.load_model import load_stylegan2ada_model_from_pkl
from app.stylegan.generation import generate_stylegan2ada_images
from app.stylegan.projection import run_projection
from app.stylegan.style_mixing import generate_style_mix

class StyleGan2ADA(StyleGanModel):
    
    folder_path = "stylegan2_ada_models/"
    loaded_models = {}

    def __init__(self, model: Model, method_options: dict):
        
        model.version = self.__class__.__name__
        self.model = self._load_model(model)
        self.method_options =  method_options
            
    def _check_for_loaded_models(self, model: Model):
        if model in self.loaded_models:
            return self.loaded_models[model]
        return False

    def _load_model(self, model: Model):
        
        stylegan2ada_model = self._check_for_loaded_models(model)

        if stylegan2ada_model:
            return stylegan2ada_model
        
        stylegan2ada_model = load_stylegan2ada_model_from_pkl(self.folder_path, model)
        self.loaded_models[model] = stylegan2ada_model

        return stylegan2ada_model

    def generate(self):
        return generate_stylegan2ada_images(self.model, self.method_options)


    def style_mix(self, row_image, col_image):
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
        Dropdown(place=1, name="Model", options=stylegan2_ada_models.models, default=0),
        Slider(place=2, name="Truncation", max=2, min=-2, step=0.1, default=1),
        Text(place=3, name="Seed", default="")
    )
)

stylemix_method = StyleGanMethod(
    name="StyleMix",
    description="Style mix different images.",
    method_options=(
        Dropdown(place=1, name="Model", options=stylegan2_ada_models.models, default=0),
        SeedOrImage(name="Row_Image", place=2, default=""),
        SeedOrImage(name="Column_Image", place=3, default=""),
        Dropdown(place=4, name="Styles", options=("Coarse", "Middle", "Fine"), default=1),
        Slider(place=5, name="Truncation", max=2, min=-2, step=0.1, default=1),
    )
)