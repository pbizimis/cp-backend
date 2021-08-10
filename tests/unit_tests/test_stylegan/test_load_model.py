from pydantic import BaseModel

from app.stylegan.load_model import load_model_from_pkl_stylegan2ada


def test_load_model_from_pkl_stylegan2ada():
    """Unit test the StyleGan2ADA loading process."""

    class MockModel(BaseModel):
        filename: str

    mock_model = MockModel(filename="img31res256fid12.pkl")

    model = load_model_from_pkl_stylegan2ada("stylegan2_ada_models", mock_model)
    assert model.mapping._get_name() == "MappingNetwork"
    assert model.synthesis._get_name() == "SynthesisNetwork"
