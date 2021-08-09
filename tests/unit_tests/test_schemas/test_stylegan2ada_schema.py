import app
from app.schemas.stylegan2ada import StyleGan2ADA
from app.schemas.stylegan_models import Model

model = Model(**{"img": 31, "res": 512, "fid": 12})


def test_stylegan2ada(mocker):

    mocker.patch(
        "app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada",
        return_value="new_model",
    )

    stylegan2ada_model = StyleGan2ADA(
        model=model, method_options={"method_option": "first_option"}
    )

    # folder to models is given
    assert type(stylegan2ada_model.folder_path) == str
    # memory db for loaded models is given
    assert type(stylegan2ada_model.loaded_models) == dict

    assert stylegan2ada_model.method_options == {"method_option": "first_option"}
    assert stylegan2ada_model.model == "new_model"
    assert model.version == "StyleGan2ADA"


def test__check_for_loaded_models():

    stylegan2ada_model = StyleGan2ADA(
        model=model, method_options={"method_option": "first_option"}
    )
    stylegan2ada_model.loaded_models[model] = "new_model"
    # check if model in memory
    assert stylegan2ada_model._check_for_loaded_models(model) == "new_model"
    assert (
        stylegan2ada_model._check_for_loaded_models(
            Model(**{"img": 30, "res": 512, "fid": 12})
        )
        == False
    )


def test__load_model(mocker):

    mocker.patch(
        "app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada",
        return_value="other_model",
    )
    stylegan2ada_model = StyleGan2ADA(
        model=model, method_options={"method_option": "first_option"}
    )
    other_model = Model(**{"img": 1, "res": 1, "fid": 1})

    # case if model is loaded from memory
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._check_for_loaded_models",
        return_value="new_model",
    )
    assert stylegan2ada_model._load_model(model) == "new_model"
    app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada.assert_not_called

    # case if model is loaded from pkl
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._check_for_loaded_models",
        return_value=False,
    )
    assert other_model not in stylegan2ada_model.loaded_models
    assert stylegan2ada_model._load_model(other_model) == "other_model"
    assert stylegan2ada_model.loaded_models[other_model] == "other_model"
    app.schemas.stylegan2ada.load_model_from_pkl_stylegan2ada.assert_called


def test_generate(mocker):
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._load_model",
        return_value="generate_model",
    )
    mocker.patch("app.schemas.stylegan2ada.generate_image_stylegan2ada")
    stylegan2ada_model = StyleGan2ADA(
        model=model, method_options={"method_option": "first_option"}
    )
    stylegan2ada_model.generate()
    app.schemas.stylegan2ada.generate_image_stylegan2ada.assert_called_once_with(
        "generate_model", {"method_option": "first_option"}
    )


def test_style_mix(mocker):
    mocker.patch(
        "app.schemas.stylegan2ada.StyleGan2ADA._load_model",
        return_value="style_mix_model",
    )
    mocker.patch("app.schemas.stylegan2ada.style_mix_two_images_stylegan2ada")
    stylegan2ada_model = StyleGan2ADA(
        model=model, method_options={"method_option": "first_option"}
    )
    stylegan2ada_model.style_mix("row_image", "col_image")
    app.schemas.stylegan2ada.style_mix_two_images_stylegan2ada.assert_called_once_with(
        "style_mix_model", {"method_option": "first_option"}, "row_image", "col_image"
    )
