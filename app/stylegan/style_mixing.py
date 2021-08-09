import os
import re
from io import BytesIO
from typing import Any, List, Union

import click
import dnnlib
import numpy as np
import PIL.Image
import torch

from app.stylegan.utils import (
    load_vector_from_bytes,
    save_image_as_bytes,
    save_vector_as_bytes,
    seed_to_array_image,
    w_vector_to_image,
)


def style_mix_two_images_stylegan2ada(
    model: Any,
    stylemix_options,
    row_image: Union[int, bytes],
    col_image: Union[int, bytes],
) -> dict:
    """Style mix two images with a stylegan2ada model.

    Args:
        model (Any): a loaded stylegan2ada model
        stylemix_options (StyleMix): an object containing stylemix options
        row_image (Union[int, bytes]): the row image as a seed or as a bytes object
        col_image (Union[int, bytes]): the column image as a seed or as a bytes object

    Returns:
        dict: a dict with the result image, the row image, and the column image and their image byte object and their feature vector byte object
    """
    device = torch.device("cpu")
    G = model
    truncation_psi = stylemix_options.truncation
    col_style_name = stylemix_options.styles
    noise_mode = "const"

    col_styles_dict = {
        "Coarse": [x for x in range(0, 2)],
        "Middle": [x for x in range(2, 6)],
        "Fine": [x for x in range(6, 14)],
    }

    col_styles = col_styles_dict[col_style_name]

    if not (isinstance(row_image, bytes) and isinstance(col_image, bytes)):

        ws = None

        if isinstance(row_image, bytes) and isinstance(col_image, int):
            ws = load_vector_from_bytes(row_image)
            row_seed = "proj_w"
            col_seed = col_image
            all_seeds = [col_seed]

        if isinstance(col_image, bytes) and isinstance(row_image, int):
            ws = load_vector_from_bytes(col_image)
            row_seed = row_image
            col_seed = "proj_w"
            all_seeds = [row_seed]

        if isinstance(col_image, int) and isinstance(row_image, int):
            col_seed = col_image
            row_seed = row_image
            all_seeds = list(set([row_seed, col_seed]))

        seed_images = []
        raw_ws = []

        for seed in all_seeds:
            image, w = seed_to_array_image(G, seed, truncation_psi)
            raw_ws.append(w)
            seed_images.append(image)

        all_w = torch.Tensor().to(device)

        seed_row_image = None
        w_row_blob = None
        seed_col_image = None
        w_col_blob = None

        if len(seed_images) == 2:
            seed_row_image = save_image_as_bytes(seed_images[0])
            w_row_blob = save_vector_as_bytes(raw_ws[0])
            seed_col_image = save_image_as_bytes(seed_images[1])
            w_col_blob = save_vector_as_bytes(raw_ws[1])
        else:
            if isinstance(row_seed, int):
                seed_row_image = save_image_as_bytes(seed_images[0])
                w_row_blob = save_vector_as_bytes(raw_ws[0])
                if isinstance(col_seed, int):
                    seed_col_image = seed_row_image
                    w_col_blob = w_row_blob

            elif isinstance(col_seed, int):
                seed_col_image = save_image_as_bytes(seed_images[0])
                w_col_blob = save_vector_as_bytes(raw_ws[0])

        for w in raw_ws[0]:
            all_w = torch.cat((all_w, w.unsqueeze(0)), 0)
        if len(raw_ws) == 2:
            for w in raw_ws[1]:
                all_w = torch.cat((all_w, w.unsqueeze(0)), 0)
        if ws is not None:
            for w in ws:
                all_w = torch.cat((all_w, w.unsqueeze(0)), 0)

    else:

        ws_col = load_vector_from_bytes(col_image)
        ws_row = load_vector_from_bytes(row_image)
        col_seed = "col_proj_w"
        row_seed = "row_proj_w"
        all_seeds = [row_seed, col_seed]
        seed_col_image = None
        w_col_blob = None
        seed_row_image = None
        w_row_blob = None

        all_w = torch.Tensor().to(device)

        for w in ws_row:
            all_w = torch.cat((all_w, w.unsqueeze(0)), 0)
        for w in ws_col:
            all_w = torch.cat((all_w, w.unsqueeze(0)), 0)

    if len(all_seeds) == 1:
        all_seeds.append("proj_w")

    w_dict = {seed: w for seed, w in zip(all_seeds, list(all_w))}

    w = w_dict[row_seed].clone()
    w[col_styles] = w_dict[col_seed][col_styles]
    w = w[np.newaxis]

    image = w_vector_to_image(G, w)

    result_image = save_image_as_bytes(image)
    result_vector = save_vector_as_bytes(w)

    return {
        "result_image": (result_image, result_vector),
        "row_image": (seed_row_image, w_row_blob),
        "col_image": (seed_col_image, w_col_blob),
    }
