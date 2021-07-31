from io import BytesIO
import PIL.Image
import torch

def save_image_as_bytes(image):
    buffer = BytesIO()
    PIL.Image.fromarray(image, "RGB").save(buffer, format="JPEG")
    return buffer.getvalue()

def save_vector_as_bytes(vector):
    buffer = BytesIO()
    torch.save(vector, buffer)
    return buffer.getvalue()

def load_bytes_vector(bytes_vector):
    buffer = BytesIO(bytes_vector)
    return torch.load(buffer)