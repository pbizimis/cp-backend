from fastapi_auth0 import Auth0
from app.core.config import AUTH0_API, AUTH0_DOMAIN

auth = Auth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API, scopes={"use:all": "Use all models"})