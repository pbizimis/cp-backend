from app.schemas.stylegan_models import Model, ModelCollection


def test_model_class(tmpdir):
    # create model from values
    model_values = {"img": 31, "res": 512, "fid": 12, "version": "version"}
    model = Model(**model_values)
    assert model.dict() == {"img": 31, "res": 512, "fid": 12, "version": "version"}
    assert model.filename == "img31res512fid12.pkl"

    # create model from filename
    model = Model.from_filename("img31res512fid12.pkl", "version_models/")
    assert model.dict() == {"img": 31, "res": 512, "fid": 12, "version": "version"}
    assert model.filename == "img31res512fid12.pkl"


def test_modelcollection_class(tmpdir):
    temp_dir = tmpdir.mkdir("stylegan_models/")
    temp_dir.join("img31res256fid12.pkl").write("1")
    temp_dir.join("img19res512fid16.pkl").write("2")
    test_models = ModelCollection(str(temp_dir) + "/")
    assert len(test_models.models) == 2
    assert test_models.models[0] == Model.from_filename(
        "img19res512fid16.pkl", str(temp_dir) + "/"
    )
    assert test_models.models[1] == Model.from_filename(
        "img31res256fid12.pkl", str(temp_dir) + "/"
    )
