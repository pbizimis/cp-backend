import json

from pydantic import BaseModel

import app
from app.stylegan.generation import generate_image_stylegan2ada


class MockGenerationOptions(BaseModel):
    truncation: float
    seed: str = None


def test_generate_image_stylegan2ada_seed(G_model, mocker):
    """Unit test the StyleGan2ADA generation process with a seed."""
    mock_options = MockGenerationOptions(truncation=0, seed=1234)

    # Stub the saving as bytes
    def return_raw_values(value):
        return str(value.tolist())

    mocker.patch(
        "app.stylegan.generation.save_image_as_bytes", side_effect=return_raw_values
    )
    mocker.patch(
        "app.stylegan.generation.save_vector_as_bytes", side_effect=return_raw_values
    )

    # Load assertion dict from file
    with open(
        "tests/unit_tests/test_stylegan/assertion_files/generation_assertion_result.txt",
        "r",
    ) as f:
        assertion_result_dict = json.loads(f.read())

    result_dict = generate_image_stylegan2ada(G_model, mock_options)
    assert result_dict["result_image"][0] == assertion_result_dict["result_image"][0]
    assert result_dict["result_image"][1] == assertion_result_dict["result_image"][1]


def test_generate_image_stylegan2ada_random(G_model, mocker):
    """Unit test the StyleGan2ADA generation process without a seed."""
    mocker.patch("app.stylegan.generation.seed_to_array_image", return_value=(0, 0))
    mocker.patch("app.stylegan.generation.save_image_as_bytes")
    mocker.patch("app.stylegan.generation.save_vector_as_bytes")
    mock_options = MockGenerationOptions(truncation=0)

    result_dict = generate_image_stylegan2ada(G_model, mock_options)

    call_args = app.stylegan.generation.seed_to_array_image.call_args
    assert call_args[0][0] == G_model
    assert call_args[0][1] in range(0, 2 ** 32 - 1)
    assert call_args[0][2] == 0.0
