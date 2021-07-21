import os
import re
from typing import List
from io import BytesIO

import click
import dnnlib
import numpy as np
import PIL.Image
import torch


def generate_style_mix(model, stylemix_options, images):

    bytes_io = BytesIO()
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

    row_image = images[0]
    col_image = images[1]

    if not (torch.is_tensor(row_image) and torch.is_tensor(col_image)):

        if torch.is_tensor(row_image) and isinstance(col_image, int):
            ws = row_image
            row_seed = "proj_w"
            col_seed = col_image
            all_seeds = [col_seed]

        if torch.is_tensor(col_image) and isinstance(row_image, int):
            ws = col_image
            col_seed = "proj_w"
            row_seed = row_image
            all_seeds = [row_seed]

        if isinstance(col_image, int) and isinstance(row_image, int):
            col_seed = row_image
            row_seed = row_image
            all_seeds = list(set([row_seed, col_seed]))

        all_z = np.stack(
            [np.random.RandomState(seed).randn(G.z_dim) for seed in all_seeds]
        )
        all_w = G.mapping(torch.from_numpy(all_z).to(device), None)

        w_avg = G.mapping.w_avg
        all_w = w_avg + (all_w - w_avg) * truncation_psi

        for w in ws:
            all_w = torch.cat((all_w, w.unsqueeze(0)), 0)

    else:

        ws_col = col_image
        ws_row = row_image
        col_seed = "col_proj_w"
        row_seed = "row_proj_w"
        all_seeds = [row_seed, col_seed]

        all_w = torch.Tensor().to(device)

        for w in ws_row:
            all_w = torch.cat((all_w, w.unsqueeze(0)), 0)
        for w in ws_col:
            all_w = torch.cat((all_w, w.unsqueeze(0)), 0)

    if len(all_seeds) == 1:
        all_seeds.append("proj_w")

    w_dict = {seed: w for seed, w in zip(all_seeds, list(all_w))}

    image_dict = {}

    w = w_dict[row_seed].clone()
    w[col_styles] = w_dict[col_seed][col_styles]
    image = G.synthesis(w[np.newaxis], noise_mode=noise_mode, force_fp32=True)
    image = (
        (image.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    )
    image = image[0].cpu().numpy()
    PIL.Image.fromarray(image, "RGB").save(bytes_io, format="JPEG")
    
    image_blob = bytes_io.getvalue()
    return image_blob
