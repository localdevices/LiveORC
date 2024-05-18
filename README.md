![Version](https://img.shields.io/github/v/release/localdevices/LiveORC)

> [!IMPORTANT]
> LiveORC is still in development. Features such as interactive selection of ground control points, assembling a camera 
> configuration and making of recipes is not yet available. To make a camera configuration, and guidance on how to 
> establish a recipe, please use pyOpenRiverCam and continue to the following sections of the user guide:
> 
> - [camera configuration](https://localdevices.github.io/pyorc/user-guide/camera_config/index.html)
> - [processing recipes](https://localdevices.github.io/pyorc/user-guide/cli.html). Scroll down until you find 
    > information on building recipes

# LiveORC
Web-based, professional and scalable velocimetry analysis for operational river monitoring with videos

# Installation
By far the easiest way to start working with LiveORC is to use docker and the liveorc.sh bash script bundled with 
the code. To use this script you will need a bash environment. Under most linux environments and macOS this is  
available as is in any terminal window you may open. Under windows, you can use the script e.g. under git bash or in 
the Windows Subsystem for Linux environment (WSL).

## Prerequisites

To install LiveORC we recommend to use Docker and the `liveorc.sh` script that comes with the code. To install 
LiveORC you will need to install the following applications (if you do not already have these).

- Git
- Docker
- Docker-compose
- Windows Subsystem for Linux (WSL 2) enabled (recommended)

Windows users should install Docker Desktop, and we recommend to use the 
[WSL 2 backend](https://docs.docker.com/desktop/wsl/). If you cannot use WSL 2, then you should give enough resources 
to run LiveORC. Normally, 4GB memory should be sufficient unless you expect many users at the same time on the web  
server. Disk storage should be set to a satisfactory amount to store the expected videos, thumbnails and keyframes.  
Note that one short video can easily be 10MB!

To install Docker, root privileges are required. The eventual user that runs LiveORC can also be non-root and this 
is our recommended use. Please take the following into account before starting LiveORC.

* The user must be part of the ``docker`` group. Please follow these
  [instructions](https://docs.docker.com/engine/install/linux-postinstall/) to ensure the user has access to the
  ``docker`` group. The typical way to add the current user to the group is by using the following:

  ```shell
  sudo usermod -aG docker $USER
  ```

* Docker usually runs as a unix socket. In most cases a non-root user will not have privileges to connect to this 
  socket. To allow the non-root user to connect to the socket, run the following to allow access:

  ```shell
  sudo chmod 666 /var/run/docker.sock
  ```

  This assumes the socket runs on `/var/run/docker.sock`. If the location is different, then alter the location.
  With these changes the non-root user should be able to run the docker containers that run as part of LiveORC.
  On Windows systems, the access to docker may have to be set in a graphical environment. Please refer to ``docker``
  documentation to allow working with docker in windows.

> [!IMPORTANT]
> Make sure you install LiveORC in a folder structure without spaces. Spaces in folder structures may result in 
> unexpected behaviour or failures. For Windows users, we recommend for instance to run LiveORC under `/c/LiveORC/` 
> directly.

## Local use

If you wish to use LiveORC on your own local network only, then the installation process is as simple as opening 
a console (in windows, please use a Git Bash console, or a WSL console) downloading the code with ``git`` and 
calling the orchestration script ``liveorc.sh``. This can be done as follows:

```shell
git clone https://github.com/localdevices/LiveORC --config core.autocrlf=input --depth 1
cd LiveORC
./liveorc.sh start
```

The process will take some time to finish, dependent on your internet connection speed. After a while, you should
see a message that you can visit ``http://localhost:8000`` to open LiveORC.

To stop LiveORC, simply press CTRL+C or run (in a separate console in the LiveORC folder):

```shell
./liveorc.sh stop
```

If you want to run LiveORC in the background and always have it start when you boot your computer and docker, you
can simply add ``--detached`` to the start command to run all container in detached mode.

## Installation for use on a public internet address.

For more scalable use on the internet you will have to expose the code on a public web address and ensure that 
traffic from and to the site is secure. To do this you need to acquire a domain name with any domain provider of 
your choice and ensure that the domain or a subdomain is forwarded to your IP address. It depends on your domain  
provider how to exactly do this. Typically, it boils down to making an 'A' record for either the entire domain or 
a subdomain and then providing your server's public IP address to the record. For instance, you may have acquired a  
domain name called freewaterdata.com and now want to have a service on subdomain liveorc.freewaterdata.com. you can  
check your public IP address e.g. on whatismyip.com or (if you use a cloud provider) check the IP address with your  
provider. Let's say your IP address is `25.26.27.28`, you then make an 'A' record for subdomain 'liveorc' and point 
it to `25.26.27.28`. 

Once the domain is linked with your server's IP address you can use the ``liveorc.sh`` script argument options to set 
everything up. Following the example domain name above:

```shell
./liveorc.sh start --hostname liveorc.freewaterdata.com --ssl
```

the `--ssl` option provides you with a Let's Encrypt certificate with automated renewal so that traffic is secured.

## Additional options for installation

### Use configured storage instead of Minio S3 bucket

By default, LiveORC will make a virtualized Minio storage bucket for you, with username `admin` and password 
`password`. Any video, keyframe or thumbnail will be stored on this bucket. You can change this to use a local folder
instead by passing the keyword `--storage-local`. This will write data to a local folder under `./media` 
(relative to the main LiveORC code folder). This is recommended only for local use.

You can also mount a local folder as the storage for the Minio storage bucket, by passing `--storage-dir` followed 
by the path (without spaces).

Alternatively, if you want to run a larger service, you may want to host files on a cloud storage, externally from
the `docker` composition. S3 buckets are supported. Provide the hostname, port, username and password by passing 
the options `--storage-host`, `--storage-port`, `--storage-user` and `--storage-pass`, all followed by the 
information needed. For instance, a cloud storage on amazon called `http://mystorage.s3.amazonaws.com` on port 80 
can be connected as follows:

```shell
./liveorc.sh start --hostname liveorc.freewaterdata.com --ssl --storage-host http://mystorage.s3.amazonaws.com 
--storage-port 80 --storage-user myuseraccount --storage-pass mysecret
```

### Use configured database

By default, LiveORC will make a virtualized PostGreSQL / PostGIS database for you, with username `postgres` and 
password `password`. Similar to the storage, this can be changed to a cloud served PostGreSQL server with PostGIS 
extensions. Make sure that you set this up yourself on a cloud storage, and then connect to the service remotely. 
This can be done in the same way as the storage settings, with similar arguments, such as shown below.

```shell
./liveorc.sh start --hostname liveorc.freewaterdata.com --ssl --db-host http://mystorage.s3.amazonaws.com 
--db-port 5432 --db-user myuseraccount --db-pass mysecret
```
In case you want to open, change and review the database directly, e.g. with [pgAdmin](https://www.pgadmin.org/), 
look for a database with the name `liveorc`.

### Debug mode

You can run LiveORC in debug mode by passing the argument `--debug` to the `liveorc.sh` start script. If you do so, 
in case anything goes wrong on rendering a page, you will receive more information about the error and the location 
in the code where this occurs. This may help to make an issue on the GitHub page. In any circumstance, do not use 
debug mode for a production server. Debug mode reveals details of the code to the user, and may therefore expose 
certain details that may make your service vulnerable.

### Setting ports

With the argument `--port` followed by an alternative port number, you can control on which port LiveORC is exposed 
on the local machine. The default is 8000 but in case this port is already taken, you may alter this. The option 
`--ssl-insecure-port-redict` controls the port to which the service is forwarded when SSL is enabled. The 
default is port 80, but you can choose to change this here. 

### Run LiveORC in the background

For a production server, you'd normally want to run LiveORC uninterrupted and in the background. To do so, add 
`--detached` to the `liveorc.sh` command.

## Stopping, or rebuilding

### Stopping the LiveORC service

Once the services have started in detached mode, you can stop the service entirely, using the command

```shell
./liveorc.sh stop
```

This stops all services including the file server and database server, if these were enabled.

### Rebuilding

If you wish to entirely rebuild LiveORC, then you may run

```shell
./liveorc.sh rebuild
```

This will only rebuild the services, not the volumes. This means that any data you may have stored will remain in 
the persistent volumes.

# Getting started

## Your first user
Once you have set up LiveOpenRiverCam, you should see a message as provided below.

```shell
liveopenrivercam  | Trying to establish communication...
liveopenrivercam  |  - - [23/Apr/2024:16:21:28 +0000] "GET / HTTP/1.0" 302 0 "-" "curl/7.88.1"
liveopenrivercam  |  - - [23/Apr/2024:16:21:29 +0000] "GET /admin/ HTTP/1.0" 302 0 "-" "curl/7.88.1"
liveopenrivercam  |  - - [23/Apr/2024:16:21:29 +0000] "GET /admin/login/?next=/admin/ HTTP/1.0" 200 16542 "-" "curl/7.88.1"
liveopenrivercam  | 
liveopenrivercam  | Congratulations! 🤩 
liveopenrivercam  | ===================
liveopenrivercam  | 
liveopenrivercam  | If there are no errors, LiveORC should be up and running!
liveopenrivercam  | 
liveopenrivercam  | Open a web browser and navigate to http://localhost:8000
liveopenrivercam  | 
```

In this case, LiveORC was run without ``--hostname`` and therefore the url is served entirely locally. Browse
to http://localhost:8000 to get to the first page.

![first_user](https://github.com/localdevices/LiveORC/assets/7658673/e368e728-aa42-4904-bc6d-c22d380c008f)

You will only see this page the very first time. It is meant to make an initial superuser! The username and password
you create here have all possibilities. Only superusers can create new users and new institutes. Superusers can also
create new superusers. Superusers can see, change or delete datasets created by any user, also users that do not 
belong to the institute of that superuser. Therefore, be careful with the creation of too many superusers.
Superuser accounts are typically needed for administrators only.

Once you have created one superuser, you will go to the main page. When you log off (see top right) you will go to a
login screen, where you can log in again with your earlier made username and password.

## Your first institute
As a user, you can:

* setup new measurement sites
* configure or reconfigure cameras on a site
* upload new cross-sections that belong to a site
* upload new recipes, that dictate how a video should be processed into analyzed velocity and discharge products.

In order to do any of these things however, you must be owner of an institute first. This is important, because
logically, a measurement site, and everything that belongs to the measurement site is owned by an institute.
Therefore, the first thing you must do, before setting up sites and things that belong to that, is set up an institute
and make yourself owner of that institute.

![add_institute](https://github.com/localdevices/LiveORC/assets/7658673/6b632b62-2e69-440f-b7d7-2d0a221e597d)

## Make your first site

Once the institute is created, you can also make a new site. You can give a site a name, an approximate coordinate 
(by clicking on the interactive map), and you must associate the site with an institute that you own.

> [!NOTE] You can also become a *member* of an institute, without owning it. In that case you can view all assets
> that belong to an institute, but you cannot add, modify or delete any of these assets. This is ideal e.g. if 
> you want to provide access to the data by an external user, that needs the data, but is not part of your team,
> or an external system that requires automated access to your data through the REST API. Delft-FEWS forecasting 
> systems for instance can directly ingest LiveORC data.

INSERT SITE PAGE

## Make a first recipe

Eventually you wish to instruct a device in the field what to do with a video, and what information to return to 
LiveORC as callback. This requires a so-called "recipe", which you need to assemble. Recipes are also used in 
[pyOpenRiverCam](https://localdevices.github.io/pyorc). In fact, we recommend to construct and test them in 
pyOpenRivercam at this moment, as we do not yet have a web interface to construct them. For further guidance on 
recipes and a full working example, we refer to the [recipe](#recipes) section.

![add_recipe](https://github.com/localdevices/LiveORC/assets/7658673/4407a981-b4fd-4c22-b683-493bc92b31d9)

# REST API

LiveORC has a full REST API behind the scenes. This is necessary to allow external devices and applications
to report on LiveORC. NodeORC makes ample use of the REST API for callbacks of results of video analyses.

The REST API also allows you to develop your own applications on top of LiveORC. For instance, if you wish
to build your own web interface around OpenRiverCam for a specific user or with a specific application in 
mind this is in principle possible! The API documentation is also disclosed automatically when you start
LiveORC. If you are on `localhost:8000`, you can find it by browsing to `http://localhost:8000/api/docs`.
The api calls are available on `http://localhost:8000/api`.


# Recipes

Recipes describe from top to bottom how a video is treated. They describe in order:
* the video - what frames to use, what the actual water level during the recording was and if frames must be stabilized
* frame preprocessing and orthorectification - several preprocessing methods can be applied to enhance 
  features, after which images are orthorectified.
* velocimetry method to use (currently only one is available, Large-Scale Particle Image Velocimetry, LSPIV)
* how to mask spurious velocities - several methods can be applied in a user-defined order
* transect extraction - uses a defined cross section with xyz coordinates to extract velocities over a cross-section 
  and compute vertically averaged velocity and discharge.
* plotting - combines a frame, 2D velocimetry and transect (1D) into a figure annotated with water level and flow 
  estimates. A user can decide if the figure is presented as orthorectified or camera perspective.

Resolution and (for LSPIV) window size are also essential parameters, but as these are typically more site specific
these are defined in the camera configuration for a given site.

>!NOTE A full recipe is provided in this file. You can directly upload and use this.

In most cases, you will not have to change a lot of things in the recipe. Below you can find a list of typical 
conditions that may require that you do change the recipe. In that case, edit the file to accomodate the changes, 
and make a new recipe with the updated file.



