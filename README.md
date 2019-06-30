# PyLops Docker
Set of Docker containers for running PyLops in different scenarios

### Docker images

* pylops_notebook: basic container to run a notebook (use pip for installing packages)
* pylops_conda_notebook: basic container to run a notebook (use conda for installing packages)
* pylops_batchjobs: container to run pylops jobs in batch

### Getting started

Create a docker environment from the directory containing the Dockerfile. For example from pylops_notebook directory:
```
docker build -t pylops-notebook .
```

Run:
```
docker images
```
you should see ``pylops-notebook`` as one of the the ``ImageID``. At this point run:
```
docker run -it -p 8888:8888 pylops-notebook
```
or
```
docker run -d -p 8888:8888 $IMAGEID
```
in detached mode and ``docker logs <container>`` to retrive the IP for the notebook.
Note that you find the name of ``<container>`` by typing ``docker container ls``.

Finally run this command to stop the container:
```
docker container stop <container>
```

You can also map a local folder into a docker folder by running:
```
docker run -d -v /path/to/local/folder:/home/jupyter/notebook -p 8888:8888 pylops-notebook
```

At this point upload the image. First we need to login:
```
docker login
```
Then we tag our image
```
docker tag pylops-notebook mrava87/pylops:notebook
```
and push it
```
docker push mrava87/pylops:notebook
```
and run it
```
docker run -it -v /path/to/local/folder:/home/jupyter/notebook -p 8888:8888 mrava87/pylops:notebook
```
We will see something like this appearing on terminal:
```
Or copy and paste one of these URLs:
    http://(c4a12e6adad3 or 127.0.0.1):8888/?token=a991d5879c7a574c8b37e1ff3934029617df09c4f71735b8
```
simply copy this to the browser by subsituting ``(c4a12e6adad3 or 127.0.0.1)`` with just
``127.0.0.1``. Moreover the first *8888* in the docker run command corresponds to the local port we
want to use. If we choose something different from 8888 we will need to also substitute that in the
path we are going to copy into the browser.

Alternatively we can use *docker-compose*. Simply move to the folder with ``docker-compose.yml`` file and run:
```
docker-compose up
```
which can be monitored via:
```
docker-compose ps
```
and stopped using:
```
docker-compose stop
```

### Useful commands
When running a container, it will always stay there unless you run it with `--rm` .
You can delete all unused resources by running:

```
docker system prune
```

and then you can remove images with

```
docker rmi $IMAGEID
```
