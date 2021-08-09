from pydantic import BaseModel


class StyleGanMethod:
    """A class that describes a stylegan method."""

    def __init__(self, name: str, description: str, method_options: tuple) -> None:
        """Init a new stylegan method.

        Args:
            name (str): the name of the method
            description (str): the description of the method
            method_options (tuple): the options of the method
        """
        self.name = name
        self.description = description
        self.method_options = method_options

    def __call__(self) -> dict:
        """Return a dict representation of the object.

        Returns:
            dict: a dict with all attributes of the object
        """
        return {
            "name": self.name,
            "description": self.description,
            "method_options": self.method_options,
        }


class Slider(BaseModel):
    """A slider method option.

    Attributes:
        type (str): the type of the method option. Defaults to slider.
        description (str): the description of the slider method option
        name (str): the name of the slider method option
        place (int): the place alongside other method options
        max (int): the max value
        min (int): the min value
        step (float): the step between max and min
        default (float): the default slider value
    """

    type: str = "slider"
    description: str = ""
    name: str
    place: int
    max: int
    min: int
    step: float
    default: float


class Dropdown(BaseModel):
    """A dropdown method option.

    Attributes:
        type (str): the type of the method option. Defaults to dropdown.
        description (str): the description of the dropdown method option
        name (str): the name of the dropdown method option
        place (int): the place alongside other method options
        options (tuple): a tuple of options
        default (float): the default dropdown value
    """

    type: str = "dropdown"
    description: str = ""
    name: str
    place: int
    options: tuple
    default: int


class Text(BaseModel):
    """A text method option.

    Attributes:
        type (str): the type of the method option. Defaults to text.
        description (str): the description of the text method option
        name (str): the name of the text method option
        place (int): the place alongside other method options
        default (float): the default text value
    """

    type: str = "text"
    description: str = ""
    name: str
    place: int
    default: str


class SeedOrImage(BaseModel):
    """A 'seed or image' method option.

    Attributes:
        type (str): the type of the method option. Defaults to seed_or_image.
        description (str): the description of the seed_or_image method option
        name (str): the name of the seed_or_image method option
        place (int): the place alongside other method options
        default (float): the default seed_or_image value
    """

    type: str = "seed_or_image"
    description: str = ""
    name: str
    place: int
    default: str
