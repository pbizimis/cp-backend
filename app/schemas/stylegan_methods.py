from pydantic import BaseModel

class StyleGanMethod():

    def __init__(self, name: str, description: str, method_options: tuple) -> None:
        self.name = name
        self.description = description
        self.method_options = method_options

    def __call__(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "method_options": self.method_options
        }

class Slider(BaseModel):
    type: str = "slider"
    description: str = ""
    name: str
    place: int
    max: int
    min: int
    step: float
    default: float

class Dropdown(BaseModel):
    type: str = "dropdown"
    description: str = ""
    name: str
    place: int
    options: tuple
    default: int

class Text(BaseModel):
    type: str = "text"
    description: str = ""
    name: str
    place: int
    default: str

class SeedOrImage(BaseModel):
    type: str = "seed_or_image"
    description: str = ""
    name: str
    place: int
    default: str