FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app /app/app
COPY ./stylegan2_ada_models /app/stylegan2_ada_models

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi-auth0