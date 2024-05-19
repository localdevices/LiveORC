![Version](https://img.shields.io/github/v/release/localdevices/LiveORC)

> [!IMPORTANT]
> LiveORC is still in development. Features such as interactive selection of ground control points, assembling a camera 
> configuration and making of recipes is not yet available. To make a camera configuration, and guidance on how to 
> establish a recipe, please use pyOpenRiverCam and continue to the following sections of the user guide:
> 
> - [camera configuration](https://localdevices.github.io/pyorc/user-guide/camera_config/index.html)
> - [processing recipes](https://localdevices.github.io/pyorc/user-guide/cli.html). Scroll down until you find 
    information on building recipes.

# LiveORC
Web-based, professional and scalable velocimetry analysis for operational river monitoring with videos

What is LiveOpenRiverCam
========================

LiveOpenRiverCam allows you to run operational measurement stations that estimate river discharge from videos.

LiveOpenRiverCam is being developed in the TEMBO Africa project. The TEMBO Africa project has received funding from the
European Union's Horizon Europe research and innovation programme under greant agreement No. 101086209.


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

> [!NOTE]
> You can also become a *member* of an institute, without owning it. In that case you can view all assets
> that belong to an institute, but you cannot add, modify or delete any of these assets. This is ideal e.g. if 
> you want to provide access to the data by an external user, that needs the data, but is not part of your team,
> or an external system that requires automated access to your data through the REST API. Delft-FEWS forecasting 
> systems for instance can directly ingest LiveORC data.

![add_site](https://github.com/localdevices/LiveORC/assets/7658673/739805ea-31c2-4598-99f4-59bbea49b26d)

## Make a first recipe

Eventually you wish to instruct a device in the field what to do with a video, and what information to return to 
LiveORC as callback. This requires a so-called "recipe", which you need to assemble. Recipes are also used in 
[pyOpenRiverCam](https://localdevices.github.io/pyorc). In fact, we recommend to construct and test them in 
pyOpenRivercam at this moment, as we do not yet have a web interface to construct them. For further guidance on 
recipes and a full working example, we refer to the [recipe](#recipes) section.

![add_recipe](https://github.com/localdevices/LiveORC/assets/7658673/4407a981-b4fd-4c22-b683-493bc92b31d9)

## Make your first camera configuration

A camera configuration contains all information about the camera perspective, lens characteristics, video 
resolution, and also the resolution of orthorectification. For geographical displaying, it also holds the
coordinate reference system of any coordinates used (not mandatory).

Currently, camera configuration cannot yet be made directly in the web interface. This is a high priority 
for future developments. Instead, you must use pyOpenRiverCam to prepare the camera configuration. We recommend
to use the command-line interface of pyOpenRiverCam to do this. We refer to the 
[camera configuration user guide](https://localdevices.github.io/pyorc/user-guide/camera_config/index.html) for
further information.

Once a camera configuration is prepared, it should be stored in a `.json` file. You can then upload this into a
new camera configuration in LiveOpenRiverCam. Go to Camera Configs and make a new one by clicking on the ➕ Add 
button in the menu. 

Besides the camera configuration itself, you can, and in most cases should provide additional details.
You can provide a name an end validity date (currently only for your own reference, in 
case you wish to move the camera or change the camera at the same site later). Also you can provide an allowed difference
in time stamp between a video that is processed with the camera configuration, and the water level associated with
the video. In case no water level is available that has a time stamp that is near enough to the video time stamp,
the video will not be processed.

You can (and should) also provide a recipe and a profile (see earlier sections) to go with the camera configuration.
And finally, you must upload the camera configuration, prepared through pyOpenRiverCam. This in total gives you
all the information required to process videos at a given site.

![add_cameraconfig](https://github.com/localdevices/LiveORC/assets/7658673/eec52ea2-5def-4635-b60a-b6aa0e0ff2cd)

Once done you can click on "Save", which brings you back to an overview of all camera configurations, managed
by you. If you want to see the result, then select the new camera configuration. You can then also see a 
geographical overview of the situation, including the bounding box of the camera configuration, and the cross
section. The cross section should overlap with your bounding box and they of course should be positioned
over the expected river section. If that is not the case, something is wrong in either the camera configuration
file or the measurements of the cross section. Carefully check if the coordinate reference system provided
with any coordinates is correct.

![change_cameraconfig](https://github.com/localdevices/LiveORC/assets/7658673/6ff13635-3821-4968-a606-428a179d7d49)

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

> [!NOTE]
> A full recipe is provided in this file. You can directly upload and use this.

In most cases, you will not have to change a lot of things in the recipe. Below you can find a list of typical 
conditions that may require that you do change the recipe. We recommend to use our template as starting point, and 
dependent on your case conditions, alter the file as needed. We describe some specific cases only. If you need more 
options and guidance please visit the [recipe section](https://localdevices.github.io/pyorc/user-guide/cli.html)
in the pyopenrivercam documentation. 

> [!WARNING]
> When changing the yaml file, make sure the YAML-syntax is followed everywhere. This means subsections (and 
> subsubsections) must be indented accurately, and double colons are used to indicate the start of a subsection. If 
> you do not follow this accurately your recipe cannot be rendered, and you'll receive errors. 

## Specify the frames and framerate that should be used

In some cases you may want to have control over the frames that are used for the analysis. By default, all frames 
available are used and framerate is read from the video metadata. Cases where you may want more control are e.g. 
follows:

* You may record long videos, and only want to use a specified set of frames
* You want to ensure that each treated video uses the same amount of frames always (in case of variable amount of 
  frames per video). 
* The first seconds may be garbage, e.g. because the camera requires autofocus, or because the camera is still 
  starting up. 
* The camera's firmware writes incorrect frames per second to the metadata (Believe us: this happens!!).

In this case, change the `video` section as follows:

```yaml
video:
  start_frame: 50  # 
  end_frame: 200
  fps: 25
```
Here we set the start and end frame to 50 and 200 respectively, and enforce that the software assumes the videos are 
25 frames per second.

## add preprocessing filters to enhance videos

The default recipe uses a temporal difference with some thresholding to remove background noise and enhance features.
This can be seen in the `frames` section. In most cases this makes moving features much, much more distinct, and you 
don't have to change a great deal. However, there are a large number of additional preprocessors available if you 
would like to use these. The rule is that you add these in subsections, with the required arguments below these 
subsections. For instance:

```yaml
frames:
  time_diff:
    abs: false
    thres: 0
  minmax:
    min: 5
  edge_detect:
    wdw_1: 2
    wdw_2: 4
```

will apply an extra edge detection step by applying a so-called "band convolution" on each frame. Basically this 
applies a smoothing using a window of 2 grid cells, and with 4 grid cells, and then subtracts the two smoothed 
results. If your tracers consist of larger patches of materials, like floating plants, this may be a useful filter.

The full list of preprocessors and how they can be applied are provided on the pyOpenRiverCam user guide in the 
[frames section](https://localdevices.github.io/pyorc/user-guide/frames/index.html).

## Masking of spurious velocimetry results

After velocimetry results are processed, spurious results should be masked out. There are many filters available to 
do this. Filters can even be applied several times, by applying mask groups as shown below. These filters usually work
well, but under certain conditions, you may decide to alter them. Some guidance is provided below.

* `minmax`: If only very low velocities occur, we suggest to alter `s_max` to a lower value. `s_max` is the maximum 
  velocity 
  you expect to occur anywhere in m/s.
* `angle`: This filter removes velocity values that are outside a certain angle tolerance. Below, the expected direction
  is set to zero (default) and the angle tolerance is 1.57 radians (90 degrees). Any velocity beyond 1.57 radians 
  will be filtered out.
* `count`: this filter counts how frequently a valid velocity is found in a given pixel. If (after all previous 
  filters) only 20% (`tolerance: 0.2`) is left, the value is assumed to be unreliable and removed. In cases where 
  very little tracers are observed, but tracers that appear are very clear, you may try to lower this value.
* `window_mean`: checks if the window average (with window size defined by `wdw`) deviates a lot from the value in the 
  cell itself. In case it deviates a lot (default is 0.7 or more, i.e. 70%), then the value is masked out. The 
  tolerance can be set with `tolerance: 0.5` to make it stricter and set it to 50%.
* `window_nan`: masks on neighbourhoods by checking how much of the neighbouring cells are missing values. By 
  default this is set to 0.7, i.e. a minimum of 70% of the surrounding cells should have values. Typically this mask 
  is applied as one of the last masks so that the other masks give a good impression of the availability of 
  information for this final mask.

```yaml
mask:
  write: True
  mask_group1:
    minmax:
      s_max: 3.0
  mask_group2:
    outliers:
      mode: and
  mask_group3:
    angle:
      angle_tolerance: 1.57
  mask_group4:
    count:
      tolerance: 0.2
  mask_group5:
    window_mean:
      wdw: 2
      reduce_time: True
  mask_group6:
    window_nan:
      wdw: 1
      reduce_time: True
```
