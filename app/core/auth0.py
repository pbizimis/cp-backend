from fastapi_auth0 import Auth0

auth = Auth0(domain="capstone-test.eu.auth0.com", api_audience="https://testapi-service-mdvcgw37oq-ew.a.run.app", scopes={"use:all": "Use all models"})