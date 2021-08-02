from app.stylegan.load_model import load_stylegan2ada_model_from_pkl
from pydantic import BaseModel

def test_load_stylegan2ada_model_from_pkl():

    class MockModel(BaseModel):
        filename: str

    mock_model = MockModel(filename="img31res256fid12.pkl")

    model = load_stylegan2ada_model_from_pkl("stylegan2_ada_models", mock_model)
    
    assert model.mapping._get_name() == "MappingNetwork"
    assert model.synthesis._get_name() == "SynthesisNetwork"
