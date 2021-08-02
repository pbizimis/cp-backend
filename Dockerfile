FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app /app/app
COPY ./stylegan2_ada_models /app/stylegan2_ada_models
COPY ./stylegan2_ada_pytorch /app/stylegan2_ada_pytorch
COPY ./requirements.txt /app/requirements.txt
COPY ./vgg16.pt /app/vgg16.pt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./requirements.txt