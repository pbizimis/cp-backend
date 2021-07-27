from fastapi_auth0 import Auth0

auth = Auth0(domain="capstone-test.eu.auth0.com", api_audience="https://api.webdesigan.com", scopes={"use:all": "Use all models"})