# Curvelops Docker distribution

This directory contains files pertaining to the Docker distribution of [Curvelops](https://github.com/PyLops/curvelops). Docker images can be found in the [Docker registry](https://hub.docker.com/r/cdacosta/curvelops).

The simplest way of getting started is running

```bash
docker-compose up
```

in a directory containing the [`docker-compose.yml`](https://github.com/pylops/pylops-docker/blob/master/curvelops_notebook/docker-compose.yml) configuration file provided.

You may also download the image and run it yourself with:

```bash
docker pull cdacosta/curvelops:latest
docker run -it -p 5000:5000 cdacosta/curvelops:latest
```

Finally, if you wish to build the image yourself, use the [`Dockerfile`](https://github.com/pylops/pylops-docker/blob/master/curvelops_notebook/Dockerfile.yml) provided. Note that you must provide FFTW 2.1.5 and CurveLab 2.3.2 source codes.
