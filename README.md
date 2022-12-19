# Geoharverster

NDGI Project Geoharvester

## Deployment

### A. Localhost deployment:

#### Frontend:

###### Requirements:

- Your favorite terminal
- Have node and npm installed (https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

###### Run:

1. cd into frontend folder ("geoharvester_frontend")
2. run `npm i` to install dependencies (from package.json)
3. run `npm start` to start the fronted on localhost (`npm start` is defined in package.json)

#### Backend:

###### Requirements:

- Your favorite terminal
- Have pip installed
- Have virtual environment in backend folder up and running (`python -m venv env &&  source ./env/bin/activate`)

###### Run:

1. cd into backend folder ("geoharvester_backend")
2. run `pip install -r requirements.txt` to install dependencies
3. run `uvicorn main:app --reload` to start server on localhost
4. Check `localhost:8000`in your browser to verify that backend is running

#### Troubleshooting:

##### VSCode does not detect venv

- https://stackoverflow.com/questions/66869413/visual-studio-code-does-not-detect-virtual-environments
