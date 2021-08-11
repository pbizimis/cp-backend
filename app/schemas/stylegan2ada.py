import random
import uuid
from typing import Any, Union

from pydantic import BaseModel, validator

from app.schemas.stylegan_methods import (
    Dropdown,
    SeedOrImage,
    Slider,
    StyleGanMethod,
    Text,
)
from app.schemas.stylegan_models import Model, StyleGanModel, stylegan2ada_models
from app.stylegan.generation import generate_image_stylegan2ada
from app.stylegan.load_model import load_model_from_pkl_stylegan2ada
from app.stylegan.projection import project_image_stylegan2ada
from app.stylegan.style_mixing import style_mix_two_images_stylegan2ada


class StyleGan2ADA(StyleGanModel):
    """A class that describes the stylegan version stylegan2ada."""

    folder_path = "stylegan2_ada_models/"
    loaded_models = {}

    def __init__(self, model: Model, method_options: dict) -> None:
        """Init a new stylegan2ada object.

        Args:
            model (Model): a model object that specifies the model that should be used for methods
            method_options (dict): a dict that contains option parameters for a stylegan method
        """
        model.version = self.__class__.__name__
        self.model = self._load_model(model)
        self.method_options = method_options

    def _check_for_loaded_models(self, model: Model) -> Union[bool, Any]:
        """Return a model if it is already loaded into memory.

        Args:
            model (Model): the model that should be loaded from memory

        Returns:
            Union[bool, Any]: either False or the loaded model
        """
        if model in self.loaded_models:
            return self.loaded_models[model]
        return False

    def _load_model(self, model: Model) -> Any:
        """Load a stylegan2ada model.

        Args:
            model (Model): the model that should be loaded

        Returns:
            Any: the loaded stylegan2ada model
        """
        stylegan2ada_model = self._check_for_loaded_models(model)

        if stylegan2ada_model:
            return stylegan2ada_model

        stylegan2ada_model = load_model_from_pkl_stylegan2ada(self.folder_path, model)
        self.loaded_models[model] = stylegan2ada_model

        return stylegan2ada_model

    def generate(self) -> dict:
        """Generate a new image with the specified stylegan2ada model."""
        return generate_image_stylegan2ada(self.model, self.method_options)

    def style_mix(
        self, row_image: Union[int, bytes], col_image: Union[int, bytes]
    ) -> dict:
        """Style mix two images with the specified stylegan2ada model."""
        return style_mix_two_images_stylegan2ada(
            self.model, self.method_options, row_image, col_image
        )


class Generation(BaseModel):
    """The stylegan2ada generation method.

    Attributes:
        name (str): the name of the method. Defaults to Generation.
        model (Model): the model that should be used for the generation
        truncation (float): the truncation value for the generation
        seed (float): the seed for the generation (can be blank to be random)
    """

    name: str = "Generation"
    model: Model
    truncation: float
    seed: str

    @validator("name")
    def name_is_default(cls, name):
        """Return the default for unity."""
        return "Generation"

    @validator("model")
    def model_is_valid(cls, model):
        """Validate the given model."""
        if model in stylegan2ada_models.models:
            return model
        raise ValueError("Please choose one of these models: " + str(stylegan2ada_models.models))

    @validator("seed")
    def seed_is_empty_or_int(cls, seed):
        """Validate that the seed is either empty or a valid int."""
        if seed == "":
            return seed
        try:
            if 0 <= int(seed) <= 4294967295:
                return seed
            raise ValueError("Seed must be between 0 and 4294967295, or blank for random.")
        except:
            raise ValueError("Seed must be between 0 and 4294967295, or blank for random.")

    @validator("truncation")
    def truncation_is_in_range(cls, truncation):
        """Validate that the truncation value is in the correct range."""
        if -2 <= truncation <= 2:
            return truncation
        raise ValueError("Truncation must be between -2 and 2.")


class StyleMix(BaseModel):
    """The stylegan2ada style mix method.

    Attributes:
        name (str): the name of the method. Defaults to StyleMix.
        model (Model): the model that should be used for the style mix
        row_image(str): a string that either is a seed (int) or an image id
        column_image(str): a string that either is a seed (int) or an image id
        styles (str): a string that defines the styles that should be used for the style mix
        truncation (float): the truncation value for the style mix
    """

    name: str = "StyleMix"
    model: Model
    row_image: str
    column_image: str
    styles: str
    truncation: float

    @validator("name")
    def name_is_default(cls, name):
        """Return the default for unity."""
        return "StyleMix"

    @validator("model")
    def model_is_valid(cls, model):
        """Validate the given model."""
        if model in stylegan2ada_models.models:
            return model
        raise ValueError("Please choose one of these models: " + str(stylegan2ada_models.models))

    @validator("row_image")
    def row_image_id_or_seed(cls, row_image):
        """Validate that the row image is either an empty string, a valid seed int or an image id."""
        if row_image == "":
            return str(random.randint(0, 2 ** 32 - 1))
        try:
            if uuid.UUID(row_image, version=4):
                return str(row_image)
        except:
            pass
        try:
            if 0 <= int(row_image) <= 4294967295:
                return str(row_image)
        except:
            pass
        raise ValueError("Row image must be empty for a random seed, a seed between 0 and 4294967295, or a valid image id.")

    @validator("column_image")
    def column_image_id_or_seed(cls, column_image):
        """Validate that the column image is either an empty string, a valid seed int or an image id."""
        if column_image == "":
            return str(random.randint(0, 2 ** 32 - 1))
        try:
            if uuid.UUID(column_image, version=4):
                return str(column_image)
        except:
            pass
        try:
            if 0 <= int(column_image) <= 4294967295:
                return str(column_image)
        except:
            pass
        raise ValueError("Column image must be empty for a random seed, a seed between 0 and 4294967295, or a valid image id.")

    @validator("styles")
    def style_is_valid(cls, styles):
        """Validate the styles string."""
        if styles == "Coarse" or styles == "Middle" or styles == "Fine":
            return styles
        raise ValueError("Styles can either be 'Coarse', 'Middle' or 'Fine'.")

    @validator("truncation")
    def truncation_is_in_range(cls, truncation):
        """Validate that the truncation value is in the correct range."""
        if -2 <= truncation <= 2:
            return truncation
        raise ValueError("Truncation must be between -2 and 2.")


# The definiton method options of the generation method.
# The definition allows to make this interface available via the API so that users or a frontend can know what inputs are allowed.
generation_method = StyleGanMethod(
    name="Generate",
    description="Generate random images or from a certain seed.",
    method_options=(
        Dropdown(
            place=1,
            name="Model",
            options=stylegan2ada_models.models,
            default=0,
            description="Choose your StyleGan2ADA model. The lower the FID value, the better the image quality.",
        ),
        Slider(
            place=2,
            name="Truncation",
            max=2,
            min=-2,
            step=0.1,
            default=1,
            description="Truncation controls how close the image is to the overall average image of the model. For example, a truncation value of 0 will always generate the same image, the average of all images that were used to train the model. The higher or lower the value, the more diverse will the image be. Be aware that an increase in image diversity means a loss in image quality. This happens because a high or low truncation value tells the model to generate an image far away from the average, which essentially is less data that the model can use to generate your image.",
        ),
        Text(
            place=3,
            name="Seed",
            default="",
            description="You can either choose an empty seed for a random generation, a specific seed value",
        ),
    ),
)
# The definiton method options of the style mix method.
# The definition allows to make this interface available via the API so that users or a frontend can know what inputs are allowed.
stylemix_method = StyleGanMethod(
    name="StyleMix",
    description="Style mix two different images. The row image will adapt the styles of the column image.",
    method_options=(
        Dropdown(
            place=1,
            name="Model",
            options=stylegan2ada_models.models,
            default=0,
            description="Choose your StyleGan2ADA model. The lower the FID value, the better the image quality.",
        ),
        SeedOrImage(
            name="Row_Image",
            place=2,
            default="",
            description="You can either choose an empty seed for a random generation, a specific seed value, or you can choose an image from your collection.",
        ),
        SeedOrImage(
            name="Column_Image",
            place=3,
            default="",
            description="You can either choose an empty seed for a random generation, a specific seed value, or you can choose an image from your collection.",
        ),
        Dropdown(
            place=4,
            name="Styles",
            options=("Coarse", "Middle", "Fine"),
            default=1,
            description="This dropdown allows to choose what kind of styles the row image adapts from the column image. Coarse styles are styles such as the content width (wide or narrow). Middle styles are structural styles such as grids, images, or text. Fine styles are almost only the color of the image.",
        ),
        Slider(
            place=5,
            name="Truncation",
            max=2,
            min=-2,
            step=0.1,
            default=1,
            description="If you decide to generate a seed, the truncation controls how close the image is to the overall average image of the model. For example, a truncation value of 0 will always generate the same image, the average of all images that were used to train the model. The higher or lower the value, the more diverse will the image be. Be aware that an increase in image diversity means a loss in image quality. This happens because a high or low truncation value tells the model to generate an image far away from the average, which essentially is less data that the model can use to generate your image.",
        ),
    ),
)
