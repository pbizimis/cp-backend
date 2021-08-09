from app.stylegan.utils import seed_to_array_image, w_vector_to_image, save_image_as_bytes, save_vector_as_bytes, load_vector_from_bytes
import json
import torch
import numpy as np
from io import BytesIO

def test_seed_to_array_image(G_model):
    result_image, result_w = seed_to_array_image(G_model, 1234, 1.0)

    with open("tests/unit_tests/test_stylegan/assertion_files/seed_to_array_assertion_result.txt", "r") as f:
        assertion_result_dict = json.loads(f.read())

    assert result_image.tolist() == assertion_result_dict["result_image"]
    assert result_w.tolist() == assertion_result_dict["result_w"]

def test_w_vector_to_image(G_model):
    
    with open("tests/unit_tests/test_stylegan/assertion_files/seed_to_array_assertion_result.txt", "r") as f:
        assertion_result_dict = json.loads(f.read())

    device = torch.device('cpu')
    w = torch.Tensor(assertion_result_dict["result_w"]).to(device)

    result_image = w_vector_to_image(G_model, w)

    assert result_image.tolist() == assertion_result_dict["result_image"]


def test_save_image_as_bytes():

    with open("tests/unit_tests/test_stylegan/assertion_files/seed_to_array_assertion_result.txt", "r") as f:
        assertion_result_dict = json.loads(f.read())

    bytes_value = save_image_as_bytes(np.array(assertion_result_dict["result_image"]))

    with open("tests/unit_tests/test_stylegan/assertion_files/save_image_as_bytes_assertion_result.txt", "rb") as f:
        assertion_bytes_value = f.read()

    assert bytes_value == assertion_bytes_value

def test_save_vector_as_bytes():

    with open("tests/unit_tests/test_stylegan/assertion_files/seed_to_array_assertion_result.txt", "r") as f:
        assertion_result_dict = json.loads(f.read())

    device = torch.device('cpu')
    w = torch.Tensor(assertion_result_dict["result_w"]).to(device)

    bytes_value = save_vector_as_bytes(w)

    with open("tests/unit_tests/test_stylegan/assertion_files/save_vector_as_bytes_assertion_result.txt", "rb") as f:
        assertion_bytes_value = f.read()

    assert type(assertion_bytes_value) == bytes
    # make sure that saved bytes ensure vector contents
    assert torch.equal(w, torch.load(BytesIO(assertion_bytes_value)))

def test_load_vector_from_bytes():

    with open("tests/unit_tests/test_stylegan/assertion_files/seed_to_array_assertion_result.txt", "r") as f:
        assertion_result_dict = json.loads(f.read())

    device = torch.device('cpu')
    w = torch.Tensor(assertion_result_dict["result_w"]).to(device)

    with open("tests/unit_tests/test_stylegan/assertion_files/save_vector_as_bytes_assertion_result.txt", "rb") as f:
        assertion_bytes_value = f.read()

    tensor = load_vector_from_bytes(assertion_bytes_value)

    assert torch.is_tensor(tensor)
    assert torch.equal(w, tensor)