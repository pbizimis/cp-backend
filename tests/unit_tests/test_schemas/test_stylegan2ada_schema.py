import app
import pytest
from app.schemas.stylegan2ada import Generation, StyleGan2ADA, StyleMix
from app.schemas.stylegan_models import Model

mock_model = Model(**{"img": 31, "res": 512, "fid": 12})


def test_stylegan2ada_init(mocker):
    """Unit test the StyleGan2ADA class object creation."""
    mocker.patch(
        "app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada",
        return_value="new_model",
    )
    mock_stylegan2ada_model = StyleGan2ADA(
        model=mock_model, method_options={"method_option": "first_option"}
    )

    assert type(mock_stylegan2ada_model.folder_path) == str
    assert type(mock_stylegan2ada_model.loaded_models) == dict
    assert mock_stylegan2ada_model.method_options == {"method_option": "first_option"}
    assert mock_stylegan2ada_model.model == "new_model"
    assert mock_model.version == "StyleGan2ADA"


def test__check_for_loaded_models():
    """Unit test the StyleGan2ADA _check_for_loaded_models method."""
    mock_stylegan2ada_model = StyleGan2ADA(
        model=mock_model, method_options={"method_option": "first_option"}
    )
    mock_stylegan2ada_model.loaded_models[mock_model] = "new_model"

    assert mock_stylegan2ada_model._check_for_loaded_models(mock_model) == "new_model"
    assert (
        mock_stylegan2ada_model._check_for_loaded_models(
            Model(**{"img": 30, "res": 512, "fid": 12})
        )
        == False
    )


def test__load_model(mocker):
    """Unit test the StyleGan2ADA _load_model method."""
    mocker.patch(
        "app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada",
        return_value="other_model",
    )
    mock_stylegan2ada_model = StyleGan2ADA(
        model=mock_model, method_options={"method_option": "first_option"}
    )
    other_model = Model(**{"img": 1, "res": 1, "fid": 1})

    # Case if model is loaded from memory
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._check_for_loaded_models",
        return_value="new_model",
    )
    assert mock_stylegan2ada_model._load_model(mock_model) == "new_model"
    app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada.assert_not_called

    # Case if model is loaded from pkl
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._check_for_loaded_models",
        return_value=False,
    )
    assert other_model not in mock_stylegan2ada_model.loaded_models
    assert mock_stylegan2ada_model._load_model(other_model) == "other_model"
    assert mock_stylegan2ada_model.loaded_models[other_model] == "other_model"
    app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada.assert_called


def test_generate(mocker):
    """Unit test the StyleGan2ADA generate method."""
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._load_model",
        return_value="generate_model",
    )
    mocker.patch("app.schemas.stylegan2ada.generate_image_stylegan2ada")
    mock_stylegan2ada_model = StyleGan2ADA(
        model=mock_model, method_options={"method_option": "first_option"}
    )
    mock_stylegan2ada_model.generate()
    app.schemas.stylegan2ada.generate_image_stylegan2ada.assert_called_once_with(
        "generate_model", {"method_option": "first_option"}
    )


def test_style_mix(mocker):
    """Unit test the StyleGan2ADA style_mix method."""
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._load_model",
        return_value="style_mix_model",
    )
    mocker.patch("app.schemas.stylegan2ada.style_mix_two_images_stylegan2ada")
    mock_stylegan2ada_model = StyleGan2ADA(
        model=mock_model, method_options={"method_option": "first_option"}
    )
    mock_stylegan2ada_model.style_mix("row_image", "col_image")
    app.schemas.stylegan2ada.style_mix_two_images_stylegan2ada.assert_called_once_with(
        "style_mix_model", {"method_option": "first_option"}, "row_image", "col_image"
    )


def test_generation_validation_name():
    """Unit test the validation of the name attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    mock_generation = Generation(name="RandomString", model=mock_model, truncation=1, seed="23")
    assert mock_generation.name == "Generation"


def test_generation_validation_model():
    """Unit test the validation of the model attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "wrong"}
    with pytest.raises(ValueError):
        Generation(name="RandomString", model=mock_model, truncation=1, seed="23")


def test_generation_validation_truncation():
    """Unit test the validation of the truncation attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    with pytest.raises(ValueError):
        Generation(name="RandomString", model=mock_model, truncation=-4, seed="23")
    with pytest.raises(ValueError):
        Generation(name="RandomString", model=mock_model, truncation=34, seed="23")


def test_generation_validation_seed():
    """Unit test the validation of the seed attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    with pytest.raises(ValueError):
        Generation(name="RandomString", model=mock_model, truncation=-4, seed="580954301894398")
    with pytest.raises(ValueError):
        Generation(name="RandomString", model=mock_model, truncation=-4, seed="Hi, Frank")


def test_stylemix_validation_name():
    """Unit test the validation of the name attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    mock_stylemix = StyleMix(name="RandomString", model=mock_model, row_image="1234", column_image="5678", styles="Middle", truncation=1)
    assert mock_stylemix.name == "StyleMix"


def test_stylemix_validation_model():
    """Unit test the validation of the model attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "wrong"}
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="1234", column_image="5678", styles="Middle", truncation=1)


def test_stylemix_validation_row_image():
    """Unit test the validation of the row image attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="Wrong", column_image="5678", styles="Middle", truncation=1)
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="-123", column_image="5678", styles="Middle", truncation=1)
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="987324569723458", column_image="5678", styles="Middle", truncation=1)


def test_stylemix_validation_column_image():
    """Unit test the validation of the column image attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="1234", column_image="Wrong", styles="Middle", truncation=1)
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="-1234", column_image="123", styles="Middle", truncation=1)
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="1234", column_image="987324569723458", styles="Middle", truncation=1)


def test_stylemix_validation_styles_image():
    """Unit test the validation of the styles attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="1234", column_image="5678", styles="NotRight", truncation=1)


def test_stylemix_validation_truncation():
    """Unit test the validation of the truncation attribute."""
    mock_model = {"img": 31, "res": 256, "fid": 12, "version": "stylegan2_ada"}
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="1234", column_image="5678", styles="Middle", truncation=-2134)
    with pytest.raises(ValueError):
        StyleMix(name="RandomString", model=mock_model, row_image="1234", column_image="5678", styles="Middle", truncation=897435987435)