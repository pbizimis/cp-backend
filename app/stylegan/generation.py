import random
import torch
import numpy as np
import PIL.Image
import base64
from io import BytesIO
from app.stylegan.utils import save_image_as_bytes, save_vector_as_bytes, seed_to_array_image
from typing import Any


def generate_stylegan2ada_images(model: Any, generation_options: dict) -> dict:

    G = model
    truncation_psi = generation_options.truncation
    seed = generation_options.seed

    if not seed:
        seed = random.randint(0,2**32-1) # 2**32-1 is the highest value

    img, w = seed_to_array_image(G, seed, truncation_psi)

    image_blob = save_image_as_bytes(img)
    w_blob = save_vector_as_bytes(w)

    return {"result_image": (image_blob, w_blob)}