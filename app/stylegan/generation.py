import base64
import random
from io import BytesIO
from typing import Any

import numpy as np
import PIL.Image
import torch

from app.stylegan.utils import (
    save_image_as_bytes,
    save_vector_as_bytes,
    seed_to_array_image,
)


def generate_image_stylegan2ada(model: Any, generation_options) -> dict:
    """Generate a new image with a stylegan2ada model.

    Args:
        model (Any): a loaded stylegan2ada model
        generation_options (Generation): an object containing generation options

    Returns:
        dict: a dict with the result image byte object and the feature vector byte object
    """
    G = model
    truncation_psi = generation_options.truncation
    seed = generation_options.seed

    if not seed:
        seed = random.randint(0, 2 ** 32 - 1)  # 2**32-1 is the highest value

    img, w = seed_to_array_image(G, seed, truncation_psi)

    image_blob = save_image_as_bytes(img)
    w_blob = save_vector_as_bytes(w)

    return {"result_image": (image_blob, w_blob)}
