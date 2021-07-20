from pydantic import BaseModel
from app.schemas.stylegan_models import stylegan2_ada_models, Model, StyleGanModel
from app.schemas.stylegan_methods import Slider, Dropdown, StyleGanMethod
from app.stylegan.load_model import load_stylegan2ada_model_from_pkl
from app.stylegan.generation import generate_stylegan2ada_images


class StyleGan2ADA(StyleGanModel):
    
    folder_path = "stylegan2_ada_models/"
    loaded_models = {}

    def __init__(self, model: Model, method_options: dict):
        
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

        list_of_images = generate_stylegan2ada_images(self.model, self.method_options)

        return list_of_images

    def style_mix(self):
        pass

class Generation(BaseModel):
    model: Model
    truncation: float

class StyleMix(BaseModel):
    model: Model
    images: list

generation_method = StyleGanMethod(
    name="Generate",
    description="Generate random images or from a certain seed.",
    method_options=(
        Dropdown(place=1, name="Model", options=stylegan2_ada_models.models, default=0),
        Slider(place=2, name="Truncation", max=2, min=-2, step=0.1, default=1)
    )
)

stylemix_method = StyleGanMethod(
    name="StyleMix",
    description="Style mix different images.",
    method_options=(
        Dropdown(place=1, name="Model", options=stylegan2_ada_models.models, default=0),
        Slider(place=2, name="Images", max=6, min=0, step=1, default=3)
    )
)