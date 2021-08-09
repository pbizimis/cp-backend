import json
import torch
from app.stylegan.projection import project_image_stylegan2ada
import app

def test_project_image_stylegan2ada(G_model, mocker):

    mocker.patch("app.stylegan.projection.project")

    with open("tests/unit_tests/test_stylegan/assertion_files/save_image_as_bytes_assertion_result.txt", "rb") as f:
        assertion_bytes_value = f.read()

    target_image_tensor = torch.load("tests/unit_tests/test_stylegan/assertion_files/projection_assertion_tensor_image.pt")
    
    assertion_proj_w = torch.load("tests/unit_tests/test_stylegan/assertion_files/projection_assertion_tensor_result.pt")
    
    proj_w = project_image_stylegan2ada(G_model, assertion_bytes_value, num_steps=5)
    call_args = app.stylegan.projection.project.call_args

    assert call_args[0][0] == G_model
    assert torch.equal(call_args[1]["target"], target_image_tensor)
    assert call_args[1]["num_steps"] == 5

def test_project(G_model, mocker):

    with open("tests/unit_tests/test_stylegan/assertion_files/save_image_as_bytes_assertion_result.txt", "rb") as f:
        assertion_bytes_value = f.read()

    assertion_proj_w = torch.load("tests/unit_tests/test_stylegan/assertion_files/projection_assertion_tensor_result.pt")
    
    proj_w = project_image_stylegan2ada(G_model, assertion_bytes_value, num_steps=5)

    assert torch.equal(proj_w, assertion_proj_w)
