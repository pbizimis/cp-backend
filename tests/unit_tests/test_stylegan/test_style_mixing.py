import json

import pytest
from pydantic import BaseModel

from app.stylegan.generation import generate_image_stylegan2ada
from app.stylegan.load_model import load_model_from_pkl_stylegan2ada
from app.stylegan.style_mixing import style_mix_two_images_stylegan2ada


# Module access to byte dict result of a generation process.
# Is needed for maximum unit test coverage.
class ByteDict:
    byte_dict = {}


class MockGenerationOptions(BaseModel):
    truncation: float
    seed: str = None


class MockStyleMixOptions(BaseModel):
    truncation: float
    styles: str


@pytest.fixture(scope="module")
def mock_saving(module_mocker):
    """Stub the saving process to bytes for easier assertion."""

    def return_raw_values(value):
        return str(value.tolist())

    module_mocker.patch(
        "app.stylegan.style_mixing.save_image_as_bytes", side_effect=return_raw_values
    )
    module_mocker.patch(
        "app.stylegan.style_mixing.save_vector_as_bytes", side_effect=return_raw_values
    )


def test_style_mix_two_images_stylegan2ada_existing(G_model, mock_saving):
    """Unit test the StyleGan2ADA style_mix process with a two existing images."""

    byte_dict = generate_image_stylegan2ada(
        G_model, MockGenerationOptions(truncation=1, seed="1234")
    )
    ByteDict.byte_dict = byte_dict

    result_stylemix_with_bytes = style_mix_two_images_stylegan2ada(
        G_model,
        MockStyleMixOptions(truncation=1, styles="Middle"),
        byte_dict["result_image"][1],
        byte_dict["result_image"][1],
    )

    with open(
        "tests/unit_tests/test_stylegan/assertion_files/style_mix_bytes_assertion_result.txt",
        "r",
    ) as f:
        assertion_result_stylemix_with_bytes = json.loads(f.read())

    assert (
        result_stylemix_with_bytes["result_image"][0]
        == assertion_result_stylemix_with_bytes["result_image"][0]
    )
    assert (
        result_stylemix_with_bytes["result_image"][1]
        == assertion_result_stylemix_with_bytes["result_image"][1]
    )
    assert result_stylemix_with_bytes["row_image"][0] == None
    assert result_stylemix_with_bytes["row_image"][1] == None
    assert result_stylemix_with_bytes["col_image"][0] == None
    assert result_stylemix_with_bytes["col_image"][1] == None


def test_style_mix_two_images_stylegan2ada_seeds(G_model, mock_saving):
    """Unit test the StyleGan2ADA style_mix process with a two images from seeds."""
    result_stylemix_with_seeds = style_mix_two_images_stylegan2ada(
        G_model, MockStyleMixOptions(truncation=1, styles="Middle"), 65473, 7453
    )

    with open(
        "tests/unit_tests/test_stylegan/assertion_files/style_mix_seeds_assertion_result.txt",
        "r",
    ) as f:
        assertion_result_stylemix_with_seeds = json.loads(f.read())

    assert (
        result_stylemix_with_seeds["result_image"][0]
        == assertion_result_stylemix_with_seeds["result_image"][0]
    )
    assert (
        result_stylemix_with_seeds["result_image"][1]
        == assertion_result_stylemix_with_seeds["result_image"][1]
    )
    assert (
        result_stylemix_with_seeds["row_image"][0]
        == assertion_result_stylemix_with_seeds["row_image"][0]
    )
    assert (
        result_stylemix_with_seeds["row_image"][1]
        == assertion_result_stylemix_with_seeds["row_image"][1]
    )
    assert (
        result_stylemix_with_seeds["col_image"][0]
        == assertion_result_stylemix_with_seeds["col_image"][0]
    )
    assert (
        result_stylemix_with_seeds["col_image"][1]
        == assertion_result_stylemix_with_seeds["col_image"][1]
    )


def test_style_mix_two_images_stylegan2ada_same_seed(G_model, mock_saving):
    """Unit test the StyleGan2ADA style_mix process with a two images from same seeds."""
    result_stylemix_with_seeds = style_mix_two_images_stylegan2ada(
        G_model, MockStyleMixOptions(truncation=1, styles="Middle"), 7453, 7453
    )

    with open(
        "tests/unit_tests/test_stylegan/assertion_files/style_mix_seeds_assertion_result.txt",
        "r",
    ) as f:
        assertion_result_stylemix_with_seeds = json.loads(f.read())

    assert (
        result_stylemix_with_seeds["result_image"][0]
        == assertion_result_stylemix_with_seeds["col_image"][0]
    )
    assert (
        result_stylemix_with_seeds["result_image"][1]
        == assertion_result_stylemix_with_seeds["col_image"][1]
    )
    assert (
        result_stylemix_with_seeds["row_image"][0]
        == assertion_result_stylemix_with_seeds["col_image"][0]
    )
    assert (
        result_stylemix_with_seeds["row_image"][1]
        == assertion_result_stylemix_with_seeds["col_image"][1]
    )
    assert (
        result_stylemix_with_seeds["col_image"][0]
        == assertion_result_stylemix_with_seeds["col_image"][0]
    )
    assert (
        result_stylemix_with_seeds["col_image"][1]
        == assertion_result_stylemix_with_seeds["col_image"][1]
    )


def test_style_mix_two_images_stylegan2ada_mix_row_col(G_model, mock_saving):
    """Unit test the StyleGan2ADA style_mix process of an existing row image and a column seed image."""
    result_stylemix_with_mixed_row_col = style_mix_two_images_stylegan2ada(
        G_model,
        MockStyleMixOptions(truncation=1, styles="Middle"),
        ByteDict.byte_dict["result_image"][1],
        7453,
    )

    with open(
        "tests/unit_tests/test_stylegan/assertion_files/style_mix_mixed_rowcol_assertion_result.txt",
        "r",
    ) as f:
        assertion_result_stylemix_with_mixed_row_col = json.loads(f.read())

    assert (
        result_stylemix_with_mixed_row_col["result_image"][0]
        == assertion_result_stylemix_with_mixed_row_col["result_image"][0]
    )
    assert (
        result_stylemix_with_mixed_row_col["result_image"][1]
        == assertion_result_stylemix_with_mixed_row_col["result_image"][1]
    )
    assert result_stylemix_with_mixed_row_col["row_image"][0] == None
    assert result_stylemix_with_mixed_row_col["row_image"][1] == None
    assert (
        result_stylemix_with_mixed_row_col["col_image"][0]
        == assertion_result_stylemix_with_mixed_row_col["col_image"][0]
    )
    assert (
        result_stylemix_with_mixed_row_col["col_image"][1]
        == assertion_result_stylemix_with_mixed_row_col["col_image"][1]
    )


def test_style_mix_two_images_stylegan2ada_mix_col_row(G_model, mock_saving):
    """Unit test the StyleGan2ADA style_mix process of an existing column image and a row seed image."""
    result_stylemix_with_mixed_col_row = style_mix_two_images_stylegan2ada(
        G_model,
        MockStyleMixOptions(truncation=1, styles="Middle"),
        65473,
        ByteDict.byte_dict["result_image"][1],
    )

    with open(
        "tests/unit_tests/test_stylegan/assertion_files/style_mix_mixed_colrow_assertion_result.txt",
        "r",
    ) as f:
        assertion_result_stylemix_with_mixed_col_row = json.loads(f.read())

    assert (
        result_stylemix_with_mixed_col_row["result_image"][0]
        == assertion_result_stylemix_with_mixed_col_row["result_image"][0]
    )
    assert (
        result_stylemix_with_mixed_col_row["result_image"][1]
        == assertion_result_stylemix_with_mixed_col_row["result_image"][1]
    )
    assert (
        result_stylemix_with_mixed_col_row["row_image"][0]
        == assertion_result_stylemix_with_mixed_col_row["row_image"][0]
    )
    assert (
        result_stylemix_with_mixed_col_row["row_image"][1]
        == assertion_result_stylemix_with_mixed_col_row["row_image"][1]
    )
    assert result_stylemix_with_mixed_col_row["col_image"][0] == None
    assert result_stylemix_with_mixed_col_row["col_image"][1] == None
