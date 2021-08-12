<p align="center">
  <img src="https://images.webdesigan.com/7977a440fb96487d9c34aa9441405929" alt="">
   <img src="https://images.webdesigan.com/9d05d12c35f54675bc03fbd331ebd218" alt="">
   <img src="https://images.webdesigan.com/638580d812d14554b0aa5bbb42b0b4cc" alt="">
</p>
<p align="center">
    <a href="https://webdesigan.com">WebDesigan, Find Inspiration</a>
  
</p>
</p>

# About The Project

This repository hosts all the backend code of my Capstone Project. The backend application is a REST API that allows interaction with StyleGan models. The corresponding frontend can be found [here](https://github.com/pbizimis/cp-frontend). However, this backend application can be used without it. If setup help is required, please contact me: philip.bizmis@code.berlin.  
_______________
The application is built around FastAPI. Other services include Redis for rate-limiting, MongoDB, and Google Cloud Storage for storage. A running production system can be found here: https://webdesigan.com. 

# Getting Started

### Setup

Please make sure that you have [Python 3.8](https://www.python.org/downloads/) installed.
_____________

Open the cp-backend-testing folder and run this command (this may take some time because the AI models are downloaded as well:
```
sh setup.sh
```

This creates a folder with the name cp-backend.
```
cd cp-backend/
```
The next step is to activate the virtual environment:
```
source venv/bin/activate
```

Update pip:
```
pip install --upgrade pip
```

For testing, an external package is required.:
```
git clone https://github.com/gonzaloverussa/pytest-async-mongodb.git
pip install pytest-async-mongodb/
rm -r pytest-async-mongodb/
```
After successful installing, please install the other requirements:
```
pip install -r ../requirements.txt
```
This concludes the setting up part of the project.
### Running
The application requires a running Redis instance on `localhost://6379`. The easiest way is to use the latest [Redis docker image ](https://hub.docker.com/_/redis) with [Docker desktop](https://www.docker.com/products/docker-desktop).  
From the root directory of the application, activate the virtual environment:
```
# /cp-backend
source venv/bin/activate
```
Open the envs.txt file in the directory above and change the first two values if necessary. The GOOGLE_APPLICATION_CREDENTIALS can work with the given configuration but might need the absolute path of your testing_credentials.json. After that, set all env variables by copying all env variables from this file:
```
envs.txt
```
You should be able to start the FastAPI test server. Please let the server listen on port 8000:
```
uvicorn app.main:app --reload
```
If everything is successful, you can access `http://localhost:8000/docs` to see the documentation for the API and interact with it.  
To authenticate the API without the frontend. Please login into Auth0 with the given account and navigate to [this page](https://manage.auth0.com/dashboard/eu/capstone-testing/apis/61146c19b0d626004693ff79/test) (Dashboard > Application > APIs > localhostapi > Test). There you can copy an access token. On http://localhost/8000/docs, click on Authorize and input the token. Now you can access the API directly.
### Testing
There are three kinds of tests that can be executed: unit, integration, and end2end tests. All tests require activating the virtual environment and setting the environment variables.
#### Unit Tests
```python
# /cp-backend
python -m pytest tests/unit_tests
```
#### Integration Tests
For integration testing, please deploy a [MongoDB instance](https://hub.docker.com/_/mongo) (`localhost:27017`) and a [Redis instance](https://hub.docker.com/_/redis) (`localhost:6379`) to Docker.
```python
# /cp-backend
python -m pytest tests/integration_tests
```
#### E2E Tests
This test also requires a running Redis instance as well as a running instance of the application on port 8000. Personally, I deployed an instance to Docker.   
Build the container with:
```python
# /cp-backend
docker build . --tag api
```
After finishing, you should be able to run the container with:
```
docker run -e MONGO_URL=$MONGO_URL -e MONGO_DB_NAME=$MONGO_DB_NAME -e MONGO_COLLECTION_NAME:$MONGO_COLLECTION_NAME -e AUTH0_DOMAIN=$AUTH0_DOMAIN -e AUTH0_API=$AUTH0_API -e GOOGLE_APPLICATION_CREDENTIALS=/app/testing_credentials.json -e REDIS_URL=redis://host.docker.internal:6379 -e REDIS_RATELIMIT_REQUESTS=100 -e REDIS_RATELIMIT_PERIOD_MINUTES=1 -p 8000:80 api
```
This command assumes that you have Redis running on Docker. The value `redis://host.docker.internal:6379` automatically connects to the right IP in Docker. If there is an issue, try `redis://localhost://6379`.  
Then run the tests with:
```python
# /cp-backend
python -m pytest end2end
```
___________
After setting up all tests, you can run all tests with:
```python
# /cp-backend
python -m pytest
```
_____________________
This setup guide is tested and should work as presented.



# Project Structure
### Overview
The repository has three main codebases: The app directory, the tests directory, and the stylegan2_ada_pytorch directory.
#### stylegan2_ada_pytorch/
The stylegan2_ada_pytorch directory has code that is copied from the official StyleGan2ADA repository and is not changed. This code is necessary to load and run stylegan2ada models. With the first model loading, this code is made available via PYTHONPATH.  
#### tests/
The tests directory holds all the test code. Unit tests run without any external setups. Narrow integration tests need a running instance of Redis and MongoDB (see Setup), and contract integration tests communicate with Auth0, MongoDB Atlas, and Google Cloud Storage. The last test directory has one end2end test that tests the API as a complete application. This requires no setup except a running instance of the application on localhost:8000. The running instance should be working with all external services (see Testing).  
#### app/
The app directory includes all code that is necessary to run the FastAPI application, as well as StyleGan code.
#### other files
In the root directory, there are two files that can be ignored. The vgg16.pt is a pytorch file that is necessary to run the projection (also included in tests). The other file is the manifest.json file. This file is only necessary for deployments from Google Cloud Build.
