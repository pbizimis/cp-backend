from app.stylegan.style_mixing import generate_style_mix
from app.stylegan.generation import generate_stylegan2ada_images
from app.stylegan.load_model import load_stylegan2ada_model_from_pkl
from pydantic import BaseModel
import json

def test_generate_style_mix(G_model, mocker):

    # prevent the saving to bytes and just return a list converted to a string for comparison
    def return_raw_values(value):
        return str(value.tolist())

    mocker.patch("app.stylegan.style_mixing.save_image_as_bytes", side_effect=return_raw_values)
    mocker.patch("app.stylegan.style_mixing.save_vector_as_bytes", side_effect=return_raw_values)


    # Mock option models
    class GenerationOptions(BaseModel):
        truncation: float
        seed: str = None

    class StyleMixOptions(BaseModel):
        truncation: float
        styles: str
    
    # Generate a real image byte dict (byte image and w vector)
    byte_dict = generate_stylegan2ada_images(G_model, GenerationOptions(truncation=1, seed="1234"))

    result_stylemix_with_bytes = generate_style_mix(G_model, StyleMixOptions(truncation=1, styles="Middle"), byte_dict["result_image"][1], byte_dict["result_image"][1])

    with open("tests/unit_tests/test_stylegan/assertion_files/style_mix_bytes_assertion_result.txt", "r") as f:
        assertion_result_stylemix_with_bytes = json.loads(f.read())

    assert result_stylemix_with_bytes["result_image"][0] == assertion_result_stylemix_with_bytes["result_image"][0]
    assert result_stylemix_with_bytes["result_image"][1] == assertion_result_stylemix_with_bytes["result_image"][1]
    assert result_stylemix_with_bytes["row_image"][0] == None
    assert result_stylemix_with_bytes["row_image"][1] == None
    assert result_stylemix_with_bytes["col_image"][0] == None
    assert result_stylemix_with_bytes["col_image"][1] == None

    result_stylemix_with_seeds = generate_style_mix(G_model, StyleMixOptions(truncation=1, styles="Middle"), 65473, 7453)

    with open("tests/unit_tests/test_stylegan/assertion_files/style_mix_seeds_assertion_result.txt", "r") as f:
        assertion_result_stylemix_with_seeds = json.loads(f.read())

    assert result_stylemix_with_seeds["result_image"][0] == assertion_result_stylemix_with_seeds["result_image"][0]
    assert result_stylemix_with_seeds["result_image"][1] == assertion_result_stylemix_with_seeds["result_image"][1]
    assert result_stylemix_with_seeds["row_image"][0] == assertion_result_stylemix_with_seeds["row_image"][0]
    assert result_stylemix_with_seeds["row_image"][1] == assertion_result_stylemix_with_seeds["row_image"][1]
    assert result_stylemix_with_seeds["col_image"][0] == assertion_result_stylemix_with_seeds["col_image"][0]
    assert result_stylemix_with_seeds["col_image"][1] == assertion_result_stylemix_with_seeds["col_image"][1]
    
    result_stylemix_with_seeds = generate_style_mix(G_model, StyleMixOptions(truncation=1, styles="Middle"), 7453, 7453)

    with open("tests/unit_tests/test_stylegan/assertion_files/style_mix_seeds_assertion_result.txt", "r") as f:
        assertion_result_stylemix_with_seeds = json.loads(f.read())

    assert result_stylemix_with_seeds["result_image"][0] == assertion_result_stylemix_with_seeds["col_image"][0]
    assert result_stylemix_with_seeds["result_image"][1] == assertion_result_stylemix_with_seeds["col_image"][1]
    assert result_stylemix_with_seeds["row_image"][0] == assertion_result_stylemix_with_seeds["col_image"][0]
    assert result_stylemix_with_seeds["row_image"][1] == assertion_result_stylemix_with_seeds["col_image"][1]
    assert result_stylemix_with_seeds["col_image"][0] == assertion_result_stylemix_with_seeds["col_image"][0]
    assert result_stylemix_with_seeds["col_image"][1] == assertion_result_stylemix_with_seeds["col_image"][1]

    result_stylemix_with_mixed_row_col = generate_style_mix(G_model, StyleMixOptions(truncation=1, styles="Middle"), byte_dict["result_image"][1], 7453)

    with open("tests/unit_tests/test_stylegan/assertion_files/style_mix_mixed_rowcol_assertion_result.txt", "r") as f:
        assertion_result_stylemix_with_mixed_row_col = json.loads(f.read())

    assert result_stylemix_with_mixed_row_col["result_image"][0] == assertion_result_stylemix_with_mixed_row_col["result_image"][0]
    assert result_stylemix_with_mixed_row_col["result_image"][1] == assertion_result_stylemix_with_mixed_row_col["result_image"][1]
    assert result_stylemix_with_mixed_row_col["row_image"][0] == None
    assert result_stylemix_with_mixed_row_col["row_image"][1] == None
    assert result_stylemix_with_mixed_row_col["col_image"][0] == assertion_result_stylemix_with_mixed_row_col["col_image"][0]
    assert result_stylemix_with_mixed_row_col["col_image"][1] == assertion_result_stylemix_with_mixed_row_col["col_image"][1]

    result_stylemix_with_mixed_col_row = generate_style_mix(G_model, StyleMixOptions(truncation=1, styles="Middle"), 65473, byte_dict["result_image"][1])

    with open("tests/unit_tests/test_stylegan/assertion_files/style_mix_mixed_colrow_assertion_result.txt", "r") as f:
        assertion_result_stylemix_with_mixed_col_row = json.loads(f.read())

    assert result_stylemix_with_mixed_col_row["result_image"][0] == assertion_result_stylemix_with_mixed_col_row["result_image"][0]
    assert result_stylemix_with_mixed_col_row["result_image"][1] == assertion_result_stylemix_with_mixed_col_row["result_image"][1]
    assert result_stylemix_with_mixed_col_row["row_image"][0] == assertion_result_stylemix_with_mixed_col_row["row_image"][0]
    assert result_stylemix_with_mixed_col_row["row_image"][1] == assertion_result_stylemix_with_mixed_col_row["row_image"][1]
    assert result_stylemix_with_mixed_col_row["col_image"][0] == None
    assert result_stylemix_with_mixed_col_row["col_image"][1] == None