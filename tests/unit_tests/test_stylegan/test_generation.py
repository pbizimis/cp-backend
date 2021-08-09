import json

from pydantic import BaseModel

import app
from app.stylegan.generation import generate_image_stylegan2ada


def test_generate_image_stylegan2ada(G_model, mocker):

    # prevent the saving to bytes and just return a list converted to a string for comparison
    def return_raw_values(value):
        return str(value.tolist())

    mocker.patch(
        "app.stylegan.generation.save_image_as_bytes", side_effect=return_raw_values
    )
    mocker.patch(
        "app.stylegan.generation.save_vector_as_bytes", side_effect=return_raw_values
    )

    class GenerationOptions(BaseModel):
        truncation: float
        seed: str = None

    mock_options = GenerationOptions(truncation=0, seed=1234)

    result_dict = generate_image_stylegan2ada(G_model, mock_options)

    with open(
        "tests/unit_tests/test_stylegan/assertion_files/generation_assertion_result.txt",
        "r",
    ) as f:
        assertion_result_dict = json.loads(f.read())

    assert result_dict["result_image"][0] == assertion_result_dict["result_image"][0]
    assert result_dict["result_image"][1] == assertion_result_dict["result_image"][1]

    # case if no seed is given

    mocker.patch("app.stylegan.generation.seed_to_array_image", return_value=(0, 0))
    mocker.patch("app.stylegan.generation.save_image_as_bytes")
    mocker.patch("app.stylegan.generation.save_vector_as_bytes")

    mock_options = GenerationOptions(truncation=0)

    result_dict = generate_image_stylegan2ada(G_model, mock_options)

    call_args = app.stylegan.generation.seed_to_array_image.call_args
    assert call_args[0][0] == G_model
    assert call_args[0][1] in range(0, 2 ** 32 - 1)
    assert call_args[0][2] == 0.0
