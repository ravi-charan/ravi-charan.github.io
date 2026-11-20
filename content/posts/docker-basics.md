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
COPY site/ /usr/share/nginx/html/
EXPOSE 80
```

- `FROM` selects a small Nginx base image.
- `COPY` adds the website files to the image.
- `EXPOSE` documents the port used by Nginx.

## 3. Build an Image and Run a Container

Run these commands from the `docker-basics` directory:

```sh
docker build -t docker-basics-web:1.0 .
docker image ls
docker run -d --name docker-basics-web -p 8080:80 docker-basics-web:1.0
docker ps
```

The `-t` option tags the image, `-d` runs the container in the background, and `-p 8080:80` maps port 8080 on the computer to port 80 in the container. Open `http://localhost:8080` to view the page.

To stop and remove the container:

```sh
docker stop docker-basics-web
docker rm docker-basics-web
```

## 4. Create and Use a Named Volume

Volumes keep data outside a container's writable layer, so it can remain available after the container is removed.

```sh
docker volume create docker-demo-data
docker volume ls
docker run --rm --mount source=docker-demo-data,target=/data alpine sh -c 'echo "Saved in a Docker volume" > /data/message.txt'
docker run --rm --mount source=docker-demo-data,target=/data alpine cat /data/message.txt
```

The second container can read the message written by the first because both use the same named volume.

## 5. Map a Host Directory

A **bind mount** maps a directory on the computer into a container. It is useful during development because host-file changes are immediately visible in the container.

The Compose example below maps `./site` to Nginx's web directory:

```yaml
volumes:
  - ./site:/usr/share/nginx/html:ro
```

Here, `:ro` makes the mounted directory read-only inside the container.

## 6. Run the App with Docker Compose

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
docker compose up --build -d
docker compose ps
docker compose logs web
```

Open `http://localhost:8080`. To stop and remove the Compose container and network:

```sh
docker compose down
```

## Key Takeaways

- A Dockerfile describes how to build an image.
- `docker build` creates an image; `docker run` starts a container from it.
- Named volumes persist Docker-managed data; bind mounts connect a host directory to a container.
- Docker Compose describes and runs a multi-container application from a YAML file.

This gives me a foundation to continue with Docker and then learn how to run containerized applications with Kubernetes.
