from pydantic import BaseModel
from app.schemas.stylegan_models import stylegan2_ada_models
from app.schemas.stylegan_methods import Slider, Dropdown, StyleGanMethod

class Generation(BaseModel):
    model: str
    truncation: float

class StyleMix(BaseModel):
    model: str
    images: list

generation_method = StyleGanMethod(
    name="Generate",
    description="Generate random images or from a certain seed.",
    method_options=(
        Dropdown(place=1, name="Models", options=stylegan2_ada_models.models, default=0),
        Slider(place=2, name="Truncation", max=2, min=-2, step=0.1, default=1)
    )
)

stylemix_method = StyleGanMethod(
    name="StyleMix",
    description="Style mix different images.",
    method_options=(
        Dropdown(place=1, name="Models", options=stylegan2_ada_models.models, default=0),
        Slider(place=2, name="Images", max=6, min=0, step=1, default=3)
    )
)