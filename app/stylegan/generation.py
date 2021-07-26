import random
import torch
import numpy as np
import PIL.Image
import base64
from io import BytesIO

def generate_stylegan2ada_images(model, generation_options: dict):

    bytes_io_image = BytesIO()
    bytes_io_w = BytesIO()
    G = model
    truncation_psi = generation_options.truncation
    seed = generation_options.seed

    if not seed:
        seed = random.randint(0,2**32-1) # 2**32-1 is the highest value

    device = torch.device('cpu')

    images = []

    z = torch.from_numpy(np.random.RandomState(int(seed)).randn(1, G.z_dim)).to(device)
    w = G.mapping(z, None, truncation_psi=truncation_psi, truncation_cutoff=8)
    img = G.synthesis(w, noise_mode='const', force_fp32=True)

    img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    final_image = PIL.Image.fromarray(img[0].cpu().numpy(), 'RGB')
    
    final_image.save(bytes_io_image, format="JPEG")
    image_blob = bytes_io_image.getvalue()

    torch.save(w, bytes_io_w)
    w_blob = bytes_io_w.getvalue()

    return {"result_image": (image_blob, w_blob)}