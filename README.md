[![Scraper](https://github.com/FHNW-IGEO/Geoharvester/actions/workflows/run_scraper.yml/badge.svg)](https://github.com/FHNW-IGEO/Geoharvester/actions/workflows/run_scraper.yml)

# NDGI Project Geoharvester

A scraper, search engine and data portal for Swiss Geoservices (WMS, WFS, WFTS).

## Add YOUR data to the project.

> [!Tip]
>
> We scrape data based on the URLs in this [source.csv file](https://github.com/FHNW-IGEO/Geoharvester/blob/main/scraper/sources.csv). If you have additional services that should be included or know of servers/urls that are no longer valid, please let us know. Either:
>
> - Open an [issue for this project](https://github.com/FHNW-IGEO/Geoharvester/issues) OR
> - Open a pull request with changes to the [source.csv](https://github.com/FHNW-IGEO/Geoharvester/blob/main/scraper/sources.csv).

## Stack & Deployment

![Stack Diagram](https://user-images.githubusercontent.com/36440175/220350037-c8300e83-8d18-4962-b99a-54b75f5c886a.PNG)

### Frontend:

###### Requirements:

- Your favorite terminal
- Have node and npm installed (https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

###### Run:

1. cd into frontend folder ("geoharvester_client")
2. run `npm i` to install dependencies (from package.json)
3. run `npm start` to start the fronted on localhost (`npm start` is defined in package.json)

---

### Backend / Database:

###### Requirements:

- Your favorite terminal
- Have docker and docker compose installed (https://docs.docker.com/compose/install/). Windows users need to install Docker Desktop (https://docs.docker.com/desktop/install/windows-install/)
- A redis.conf in /server/app/redis with the setting requirepass= set to a password. Create the file manually, it must not be checked into git.
- A redis.env in /server/app/redis with REDIS_HOST_PASSWORD= set to a password. Create the file and its content manually, it must not be checked into git.

###### Run:

1. cd into server folder
2. Run `docker compose --env-file ./app/redis/redis.env  up --build` (this takes a while for the first build). Make sure to use `docker compose` not the (soon to be) depricated `docker-compose`
3. Check `localhost:8000/api`in your browser to verify that backend is running

#### Troubleshooting:

<details>
  <summary>Expand</summary>

##### Cannot start Docker from terminal

- Error `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?` Start docker process with `sudo service docker start`

##### Cannot start application

- Check that you are starting the backend from the `server` folder (not server/apps). Is Docker running? You might need to start the daemon (Ubuntu: `sudo service docker start`) or Docker Desktop (Windows)
- Make sure that you have created the two files that contain the redis password, as described above.
- Use `docker compose --env-file ./app/redis/redis.env  up --build` (or another path to where the redis password is located).

##### NGINX not (re)starting

This can happen if the server became unresponsive when building the frontend.
The eror iss something like `Job for nginx.service failed because the control process exited with error code.` without any more info.
Run `sudo killall apache2` to kill any process still running and blocking the restart of NGING, then run `sudo service nginx restart` to restart NGINX.

##### Error about reaching max_clients and no results in the frontend.

Redis allows a limit of 10000 by default and will throw an error if the limit is set to a higher number in code. In order to allow a higher limit, this needs to be set in the redis .conf file and the modified config needs to be copied to the docker instance (which is handled by docker-compose.yml, "volumes" ). Redis v.7.0+ required.

#### Development / VSCode Support:

Docker is set up to automatically copy code changes into the container. However, when it comes to the Python interpreter and the management of dependencies on your local machine both (Docker and your local environment) are not in sync by default. VSCode might flag missing dependencies on your local environment, depending on which interpreter is selected. There are two approaches to solve this issue for development:

a) You can either set up a venv and install the dependencies from requirements.txt (cd into server/app, then run `python -m venv env &&  source ./env/bin/activate && pip install -r requirements.txt`), then point the Python interpreter of VSCode to it. Make sure to rerun `pip install` if you make changes to the requirements file.

b) For a "single source of truth" approach, install the "dev containers" extension for VSCode (https://code.visualstudio.com/docs/devcontainers/containers), then attach to the container (https://code.visualstudio.com/docs/devcontainers/attach-container). Windows user: This requires Docker Desktop with WSL 2 set up.

</details>

---

## API Documentation

#### SwaggerUI

Fast API comes with Swagger UI preinstalled. If you have the backend running (see steps above), Swagger UI is available on http://localhost:8000/api/docs. See the wiki pages of this repository for the documentation of this project.
