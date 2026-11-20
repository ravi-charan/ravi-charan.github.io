---
title: "Docker Basics: Images, Volumes, and Compose"
date: 2026-11-20
draft: false
tags:
  - docker
  - devops
  - containers
---

## What I Learned Today

Today I started learning Docker fundamentals: writing a Dockerfile, building an image, running a container, mapping storage, and using Docker Compose.

An **image** is a packaged template. A **container** is a running instance of that image.

> These examples assume Docker Desktop or Docker Engine is installed and running.

## 1. Create a Small Web App

Create this directory structure:

```text
docker-basics/
├── Dockerfile
├── compose.yaml
└── site/
    └── index.html
```

Add a simple page in `site/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>My Docker Demo</title>
  </head>
  <body>
    <h1>Hello from Docker!</h1>
    <p>This page is served by an Nginx container.</p>
  </body>
</html>
```

## 2. Create a Dockerfile

A Dockerfile contains the steps Docker uses to build an image:

```dockerfile
FROM nginx:alpine
ARG APP_VERSION=1.0
LABEL org.opencontainers.image.title="docker-basics-web" \
      org.opencontainers.image.version="${APP_VERSION}"
WORKDIR /usr/share/nginx/html
COPY site/ ./
RUN nginx -t
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

- `FROM` selects a small Nginx base image.
- `ARG` defines a value that can be set while building the image.
- `LABEL` stores searchable image metadata.
- `WORKDIR` sets the working directory for following instructions.
- `COPY` adds the website files to that directory in the image.
- `RUN` checks the Nginx configuration while the image is being built.
- `EXPOSE` documents the port used by Nginx.
- `HEALTHCHECK` periodically checks that Nginx responds to an HTTP request.
- `CMD` sets the default command that starts Nginx when the container runs.

## 3. Build an Image and Run a Container

Run these commands from the `docker-basics` directory:

```sh
docker version
docker build --build-arg APP_VERSION=1.0 -t docker-basics-web:1.0 .
docker image ls
docker image inspect docker-basics-web:1.0
docker run -d --name docker-basics-web -p 8080:80 docker-basics-web:1.0
docker ps
```

The `-t` option tags the image, `-d` runs the container in the background, and `-p 8080:80` maps port 8080 on the computer to port 80 in the container. Open `http://localhost:8080` to view the page.

To try a different build argument, build another image version:

```sh
docker build --build-arg APP_VERSION=1.1 -t docker-basics-web:1.1 .
```

After the container starts, Docker shows its health state in `docker ps`. You can also check it directly:

```sh
docker inspect --format "{{.State.Health.Status}}" docker-basics-web
```

## 4. Inspect and Manage Containers

These commands help inspect the running web container:

```sh
docker ps -a
docker logs --tail 50 docker-basics-web
docker exec -it docker-basics-web sh
docker inspect docker-basics-web
docker stats --no-stream docker-basics-web
```

`docker exec -it ... sh` opens a shell inside the running container. Type `exit` to leave it. `docker logs` shows application output, and `docker stats` shows resource use.

Stop and remove the container when finished:

```sh
docker stop docker-basics-web
docker rm docker-basics-web
```

## 5. Create and Use a Named Volume

Volumes keep data outside a container's writable layer, so it can remain available after the container is removed.

```sh
docker volume create docker-demo-data
docker volume ls
docker volume inspect docker-demo-data
docker run --rm --mount source=docker-demo-data,target=/data alpine sh -c 'echo "Saved in a Docker volume" > /data/message.txt'
docker run --rm --mount source=docker-demo-data,target=/data alpine cat /data/message.txt
```

The second container can read the message written by the first because both use the same named volume.

## 6. Map a Host Directory

A **bind mount** maps a directory on the computer into a container. It is useful during development because host-file changes are immediately visible in the container.

The Compose example below maps `./site` to Nginx's web directory:

```yaml
volumes:
  - ./site:/usr/share/nginx/html:ro
```

Here, `:ro` makes the mounted directory read-only inside the container.

## 7. Connect Containers with a Network

A user-defined network lets containers reach each other by container name:

```sh
docker network create docker-demo-net
docker network ls
docker run -d --name web-one --network docker-demo-net nginx:alpine
docker run --rm --network docker-demo-net busybox:1.36 wget -qO- http://web-one
docker network inspect docker-demo-net
docker rm -f web-one
docker network rm docker-demo-net
```

The temporary BusyBox container requests the Nginx page using `web-one` as its hostname. The user-defined network provides that name lookup.

## 8. Run the App with Docker Compose

Create `compose.yaml`:

```yaml
services:
  web:
    build: .
    ports:
      - "8080:80"
    volumes:
      - ./site:/usr/share/nginx/html:ro
```

Compose builds the image and starts the service:

```sh
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs -f web
docker compose exec web sh
docker compose restart web
```

Type `exit` to leave the shell, then open `http://localhost:8080`. To stop and remove the Compose container and network:

```sh
docker compose down
```

## 9. Build a Python API Image

The earlier example serves static files with Nginx. This second example packages a small FastAPI app and runs it as a non-root user.

The runnable example is also in the repository under `examples/python-api/`. Its directory structure is:

```text
examples/python-api/
├── Dockerfile
├── requirements.txt
└── src/
    └── app/
        ├── __init__.py
        └── main.py
```

In `requirements.txt`, list the Python packages:

```text
fastapi
uvicorn[standard]
```

In `src/app/main.py`, create a small API:

```python
from fastapi import FastAPI

app = FastAPI(title="Docker Learning API")


@app.get("/")
def home():
    return {"message": "The API is running in Docker"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

The `Dockerfile`:

```dockerfile
# Base image
FROM python:3.13

# Set working directory
WORKDIR /usr/local/app

# Copy dependency list and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src ./src

# Make app.main importable from the src directory
ENV PYTHONPATH=/usr/local/app/src

# Expose application port
EXPOSE 8080

# Create a non-root user and give it access to the application files
RUN useradd --create-home app && chown -R app:app /usr/local/app
USER app

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

`PYTHONPATH` is needed because the Python package is under `src/`. `EXPOSE` documents the app's port; `-p` below publishes it on the host. `USER app` runs the service without root privileges.

From the repository root, build and run the image:

```sh
cd examples/python-api
docker build -t python-api:1.0 .
docker image ls
docker run -d --name python-api -p 8080:8080 python-api:1.0
docker ps
docker logs python-api
```

Open `http://localhost:8080` to see the response or `http://localhost:8080/docs` to explore the API. Stop and remove the container when finished:

```sh
docker stop python-api
docker rm python-api
```

## 10. Check Docker Disk Usage

```sh
docker system df
```

This shows disk space used by images, containers, and volumes. Review data before using cleanup commands such as `docker volume rm` or `docker system prune`, since removing volumes or unused resources can delete data you may want to keep.

## Key Takeaways

- A Dockerfile describes how to build an image.
- `docker build` creates an image; `docker run` starts a container from it.
- Named volumes persist Docker-managed data; bind mounts connect a host directory to a container.
- Docker Compose describes and runs a multi-container application from a YAML file.

This gives me a foundation to continue with Docker and then learn how to run containerized applications with Kubernetes.
