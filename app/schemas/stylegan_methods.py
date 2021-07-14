from pydantic import BaseModel

class StyleGanMethod():

    def __init__(self, name: str, description: str, method_options: tuple):
        self.name = name
        self.description = description
        self.method_options = method_options

    def __call__(self):
        return {
            "name": self.name,
            "description": self.description,
            "method_options": self.method_options
        }

class Slider(BaseModel):
    type: str = "slider"
    name: str
    place: int
    max: int
    min: int
    step: float
    default: float

class Dropdown(BaseModel):
    type: str = "dropdown"
    name: str
    place: int
    options: tuple
    default: int