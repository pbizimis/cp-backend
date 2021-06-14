from fastapi import APIRouter

router = APIRouter()

@router.get("/random")
def generate_image():
    return {"message": "Generated!"}