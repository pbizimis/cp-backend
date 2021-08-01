import os
import re
from typing import List
from io import BytesIO

import click
import dnnlib
import numpy as np
import PIL.Image
import torch
from app.stylegan.utils import save_image_as_bytes, save_vector_as_bytes, load_bytes_vector, seeds_to_array_images, w_vector_to_image

def generate_style_mix(model, stylemix_options, row_image, col_image):

    device = torch.device("cpu")
    G = model
    truncation_psi = stylemix_options.truncation
    col_style_name = stylemix_options.styles
    noise_mode = "const"

    col_styles_dict = {
        "Coarse": [x for x in range(0,2)],
        "Middle": [x for x in range(2,6)],
        "Fine": [x for x in range(6,14)]
    }

    col_styles = col_styles_dict[col_style_name]

    if not (isinstance(row_image, bytes) and isinstance(col_image, bytes)):

        ws = None

        if isinstance(row_image, bytes) and isinstance(col_image, int):
            ws = load_bytes_vector(row_image)
            row_seed = "proj_w"
            col_seed = col_image
            all_seeds = [col_seed]

        if isinstance(col_image, bytes) and isinstance(row_image, int):
            ws = load_bytes_vector(col_image)
            col_seed = "proj_w"
            row_seed = row_image
            all_seeds = [row_seed]

        if isinstance(col_image, int) and isinstance(row_image, int):
            col_seed = col_image
            row_seed = row_image
            all_seeds = list(set([row_seed, col_seed]))

        seed_images, all_w = seeds_to_array_images(G, all_seeds, truncation_psi)
        
        if len(seed_images) == 2:
            seed_row_image = save_image_as_bytes(seed_images[0])
            w_row_blob = save_vector_as_bytes(all_w[0])
            seed_col_image = save_image_as_bytes(seed_images[1])
            w_col_blob = save_vector_as_bytes(all_w[1])
        else:
            if isinstance(row_seed, int) and isinstance(col_seed, int):
                seed_row_image = save_image_as_bytes(seed_images[0])
                w_row_blob = save_vector_as_bytes(all_w[0])
                seed_col_image = seed_row_image
                w_col_blob = w_row_blob
            elif isinstance(row_seed, int):
                seed_row_image = save_image_as_bytes(seed_images[0])
                w_row_blob = save_vector_as_bytes(all_w[0])
                seed_col_image = None
                w_col_blob = None
            elif isinstance(col_seed, int):
                seed_row_image = None
                w_row_blob = None
                seed_col_image = save_image_as_bytes(seed_images[0])
                w_col_blob = save_vector_as_bytes(all_w[0])
        
        if ws is not None:
            for w in ws:
                all_w = torch.cat((all_w, w.unsqueeze(0)), 0)


    else:

        ws_col = load_bytes_vector(col_image)
        ws_row = load_bytes_vector(row_image)
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

    return {"result_image": (result_image, result_vector), "row_image": (seed_row_image, w_row_blob), "col_image": (seed_col_image, w_col_blob)}
