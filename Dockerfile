FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app /app/app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi-auth0