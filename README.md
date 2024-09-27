<figure>
    <img src="https://raw.githubusercontent.com/localdevices/pyorc/main/docs/_static/orc_logo_color.svg" 
width=100 align="right">
</figure>
<br>

![Version](https://img.shields.io/github/v/release/localdevices/LiveORC)

# LiveORC
Web-based, professional and scalable velocimetry analysis for operational river monitoring with videos.

* [What is LiveOpenRiverCam](#what-is-liveopenrivercam)
* [Installation](#installation)
  * [Prerequisites](#prerequisites)
  * [Local use](#local-use)
  * [Additional options for installation](#additional-options-for-installation)
  * [Stopping or rebuilding](#stopping-or-rebuilding)
* [Getting started](#getting-started)
  * [Your first user](#your-first-user)
  * [Your first institute](#your-first-institute)
  * [Make your first site](#make-your-first-site)
  * [Make a first recipe](#make-a-first-recipe)
  * [Add a first profile](#add-a-first-profile)
  * [Make your first camera configuration](#make-your-first-camera-configuration)
  * [Upload a new video for processing](#upload-a-new-video-for-processing)
  * [Adding a water level to the video](#adding-a-water-level-to-the-video)
  * [Processing your video](#processing-your-video)
  * [Results](#results)
  * [What next](#what-next)
* [Set up a field camera](#set-up-a-field-camera)
* [REST API](#rest-api)
* [Recipes](#recipes)
* [Trademark](#trademark)

> [!IMPORTANT]
> LiveORC is still in development. Features such as interactive selection of ground control points, assembling a camera 
> configuration and making of recipes is not yet available. To make a camera configuration, and guidance on how to 
> establish a recipe, please use pyOpenRiverCam and continue to the following sections of the user guide:
> 
> - [camera configuration](https://localdevices.github.io/pyorc/user-guide/camera_config/index.html)
> - [processing recipes](https://localdevices.github.io/pyorc/user-guide/cli.html). Scroll down until you find 
    information on building recipes.

# What is LiveOpenRiverCam

LiveOpenRiverCam allows you to run operational measurement stations that estimate river surface velocity and discharge 
from videos. It is meant for e.g. National HydroMeteorological Societies (NHMS), hydropower authorities, waterboards,
or service providers of such entities, who wish to establish their own services for such users. It is for anyone who 
wishes to operationalize image-based river surface velocity and discharge measurements using an entirely
open source, open scientific transparent approach. You can start working with LiveORC with an internet connection,
a desktop or laptop computer and one hour of time! You can scale the work to many server instances once being 
familiarized with the components and methods.

LiveORC will provide you with the following functionalities:
* An administration-style front end for managing sites, configuration, videos and time series.
* Visualization of time series and video analyses.
* Fully automated data streaming from operational camera/water level feeds in the field with "edge processing".
* Per-video processing through "cloud processing". 
* A very fast and easy start to this all, through convenient virtualization of services and a very easy to use set up 
  script.

Processing on sites ("edge processing") or on cloud nodes ("cloud processing") is performed by
[NodeOpenRiverCam](https://github.com/localdevice/nodeorc), the node processing tool around OpenRiverCam. The 
processing methods read videos, select frames, enhance features, orthorectify and estimates surface velocity 
and discharge using state-of-the-art velocimetry methods. NodeOpenRiverCam is included in LiveORC, so deployment is 
very easy and automated.

# Acknowledgements

> [!IMPORTANT] 
> LiveOpenRiverCam is being developed in the TEMBO Africa project. The TEMBO Africa project has received 
> funding from the European Union's Horizon Europe research and innovation programme under grant agreement No.101086209.  
> We have also received funding from the WMO HydroHub program. This funding was used to conceptualise and pilot 
> OpenRiverCam. The test dataset was collected in close collaboration with the Waterboard Limburg. We 
> greatly appreciate the continuing collaboration with the waterboard. Finally, our deployment script is based to a 
> large extent on the great work of the WebOpenDroneMap team. We also acknowledge their great work.

# Installation
By far the easiest way to start working with LiveORC is to use docker and the `liveorc.sh` bash script bundled with 
the code. The script is strongly based on the deployment script of 
[WebOpenDroneMap](https://github.com/OpenDroneMap/WebODM/). To use this script you will need a so-called bash 
environment. Under most linux environments and macOS this is available as is in any terminal window you may open. 
Under windows, you can use the script e.g. under git bash or in the Windows Subsystem for Linux environment (WSL).

The idea of this script is that as a user, you do not need to know all the details about the services that are 
required to set up the LiveORC. These services include:
- the web dashboard,
- the database, storing sites, time series, video metadata, but also users, institutes and their accessibility to 
  videos, time series and any other assets,
- compute nodes, equipped with [NodeOpenRiverCam](https://github.com/localdevices/nodeorc). The more you have the 
  more videos can be processed at the same time,
- a cloud storage volume.

Without any additional arguments, `liveorc.sh` automatically sets up all these services in a virtualized manner on your 
machine using the `Docker` ecosystem. Once you are ready to scale your operations by hosting all services on 
dedicated machines, and not locally but in the cloud, you can do so by providing additional arguments in the 
`liveorc.sh` script. 

## Prerequisites

To install LiveORC we recommend to use Docker and the `liveorc.sh` script that comes with the code. To install 
LiveORC you will need to install the following applications first (if you do not already have these).

- (For Windows users only:) Windows Subsystem for Linux (WSL 2) enabled (recommended)
- [Git](https://git-scm.com/downloads)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker-compose](https://docs.docker.com/compose/install/)

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

### More processing nodes

By default, one processing node, equipped with NodeORC is installed on the same machine. You can extend this with the
option `--nodes` followed by the number of nodes you wish to deploy. You can in principle also deploy nodes remotely 
but currently we do not yet have a separate API for running these. This means that your entire LiveORC environment 
details must be present on that remote node, including all passwords. This is potentially a security risk. We have 
plans to write a separate API for NodeORC so that remote nodes do not need passwords, but can simply be monitored 
through their own API.

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

This stops all services including the file server and database server, if these were enabled. If you restart your
computer, the services will start again, if you have started them in detached mode. You can also entirely disable 
the services again by issuing:
```shell
./liveorc.sh down
```

### Rebuilding

If you wish to entirely rebuild LiveORC, then you may run

```shell
./liveorc.sh rebuild
```

This will only rebuild the services, not the volumes. This means that any data you may have stored will remain in 
the persistent volumes.

# Getting started

Let's get started! You want to get a feel of what LiveORC can do for you. We are going through a top-to-bottom 
process of making your first user, site, camera configuration and a first processed video. It is important to 
understand that the intention of LiveORC is to do end-to-end processing, but also to allow processing of many videos 
on the same site, taken with the same camera with the same perspective. Therefore, the steps of creating a user, an 
institute, a site, a profile (for measuring cross-section discharge), a recipe and a camera configuration, only need 
to be done once for a single site with a fixed camera. After that you can simply feed videos manually or through the 
API or (with a device in the field, more about that later) from NodeOpenRiverCam.

Please download the test dataset by downloading this dataset:

[liveorc_sample_data.zip](https://github.com/user-attachments/files/15514803/liveorc_sample_data.zip)

From here onwards, we assume that you have started the entire stack locally with the following command.

```shell
./liveorc.sh start --detached
```
With this, your server components all start in the background. Remember that the services will keep on running, even 
if you reboot your machine!! If you want to stop the services until the next reboot, please issue:

```shell
./liveorc.sh stop
```

When you want to permanently shut down the services until you actively start them again issue:

```shell
./liveorc.sh down
```

> [!NOTE]
> From here onwards, if you want to really quickly get an impression without being bothered by explanations, please 
> only look at the blocks of text, that are highlighted with a NOTE indicator, such as this text. If you want to 
> properly understand what's going, then please also read all intermediate texts.

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
Superuser accounts are typically needed for administrators only, and can be the cause of vulnerabilities of your 
infrastructure.

> [!NOTE]
> Create your first super user by filling in the details in the very first start screen. You will not see this 
> screen again (unless you entirely delete your database 😉). Your email address will be your username. 

Once you have created one superuser, you will go to the main page. When you log off (see top right) you will go to a
login screen, where you can log in again with your earlier made username (email) and password.

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

> [!NOTE]
> Under the "Users and institutes" menu section, click on the ➕ Add button of the "Institutes" menu item. Create an 
> institute by selecting yourself as an owner, and by providing a name with your institute. 


![add_institute](https://github.com/localdevices/LiveORC/assets/7658673/6b632b62-2e69-440f-b7d7-2d0a221e597d)

> [!TIP]
> You can also become a *member* of an institute, or (as super user) make another user member of an institute, without 
> owning it. In that case you can view all assets that belong to an institute, but you cannot add, modify or delete any
> of these assets. This is ideal e.g. if you want to provide access to the data by an external user, that needs the 
> data, but is not part of your team, or an external system that requires automated access to your data through the 
> REST API. Delft-FEWS forecasting systems for instance can directly ingest LiveORC data.

## Make your first site

Once the institute is created, you must also make a new site, as any video, camera configuration object, or time series
must belong to a site eventually. 

> [!NOTE]
> Under the "Assets" menu section, click on the ➕ Add button of the "Sites" menu item. You can give a site a name, an 
> approximate coordinate (by clicking on the interactive map), and you must associate the site with an institute 
> that you own. Select the institute you just created.

![add_site](https://github.com/localdevices/LiveORC/assets/7658673/739805ea-31c2-4598-99f4-59bbea49b26d)

## Make a first recipe

Eventually you wish to instruct a device in the field what to do with a video, and what information to return to 
LiveORC as callback. This requires a so-called "recipe", which you need to assemble. Recipes are also used in 
[pyOpenRiverCam](https://localdevices.github.io/pyorc). In fact, we recommend to construct and test them in 
pyOpenRiverCam at this moment, as we do not yet have a web interface to construct them. For further guidance on 
recipes and a full working example, we refer to the [recipe](#recipes) section.

> [!NOTE]
> Under the "Assets" menu section, click on the ➕ Add button of the "Recipes" menu item. You can give a recipe a name,
> associate it with an institute that you own and select the recipe file (.YAML formatted). Here, use the file 
> `recipe.yml`, provided in the test dataset. 

![add_recipe](https://github.com/localdevices/LiveORC/assets/7658673/4407a981-b4fd-4c22-b683-493bc92b31d9)

## Add a first profile

In a very similar way, you can also add a profile. The profile consists of a set of x, y, z points describing the 
cross-section of the stream you are observing. The cross-section naturally has to be located as much as possible within 
the objective that your camera is looking at, and must be measured using the same coordinate system as your control 
points. Note that also the vertical datum MUST be the same. It is not a problem if a part of the profile is 
partly outside the objective. In fact, this can easily occur in rivers with a very wide floodplain, that only 
occasionally inundates. This then means that if those sections become inundated, velocity in those sections will 
be estimated through infilling techniques.

> [!NOTE]
> Under the "Assets" menu section, click on the ➕ Add button of the "Profiles" menu item. You can give a profile a name,
> associate it with a site that you own and select the profile file (.geojson formatted). Here, use the file 
> `profile.geojson`, provided in the test dataset. Once you click "SAVE" you will see a new profile in the menu. If 
> you click it you can inspect the profile on a geographical map. 

## Make your first camera configuration

A camera configuration contains all information about the camera perspective, lens characteristics, video 
resolution, and also the resolution of orthorectification. For geographical displaying, it also holds the
coordinate reference system of any coordinates used (not mandatory).

Currently, camera configuration cannot yet be made directly in the web interface. This is a high priority 
for future developments. Instead, you must use pyOpenRiverCam to prepare the camera configuration. We recommend
to use the command-line interface of pyOpenRiverCam to do this. We refer to the 
[camera configuration user guide](https://localdevices.github.io/pyorc/user-guide/camera_config/index.html) for 
further information.

Once a camera configuration is prepared within pyOpenRiverCam, it is stored in a `.json` file. You can then upload this 
into a new camera configuration in LiveOpenRiverCam. The test dataset contains a camera config .json file that was 
made for the camera view of the video of the test dataset. 

> [!NOTE]
> Under the "Assets" menu section, click on the ➕ Add button of the "Camera configs" menu item. You can give a 
> camera configuration a name (easy to recognise) and associate it with a site. Through the site, it will also 
> become associated with the institute owning that site. Besides the camera configuration itself, you can, and in most
> cases should provide additional details.
> You can provide a name an end validity date (currently only for your own reference, in 
> case you wish to move the camera or change the camera at the same site later). Also you can provide an allowed 
> difference in time stamp between a video that is processed with the camera configuration, and the water level 
> associated with the video. In case no water level is available that has a time stamp that is near enough to the 
> video time stamp, the video cannot yet be processed as a water level is essential for processing a video.
> You can (and should) also provide a recipe and a profile (see earlier sections) to go with the camera configuration.
> And finally, you must upload the camera configuration, prepared through pyOpenRiverCam. Here provide the file 
> `cameraconfig.json` from the test dataset. This in total gives you all the information required to process videos at 
> a given site. Click on "SAVE" to store your selections.

![add_cameraconfig](https://github.com/localdevices/LiveORC/assets/7658673/eec52ea2-5def-4635-b60a-b6aa0e0ff2cd)

Once done you will be brought back to an overview of all camera configurations, managed
by you. If you want to see the result, then select the new camera configuration. You can then also see a 
geographical overview of the situation, including the bounding box of the camera configuration, and the 
cross-section. The cross-section should overlap with your bounding box and they of course should be positioned
over the expected river section. If that is not the case, something is wrong in either the camera configuration
file or the measurements of the cross-section. Carefully check if the coordinate reference system provided
with any coordinates is correct. Again, also ensure that the vertical datum of ground control points and cross 
section is the same! This is a typical error made, and essential to correct in order to get good results.

![change_cameraconfig](https://github.com/localdevices/LiveORC/assets/7658673/6ff13635-3821-4968-a606-428a179d7d49)

## Upload a new video for processing

You are now ready to upload videos into LiveORC, which are aware of the site and camera configuration they apply to.

> [!NOTE]
> Under the "Assets" menu section, click on the ➕ Add button in the "Video" menu item. Now select the video file from 
> the sample dataset `schedule_20220830_133706.mp4` and select you newly made camera configuration. You must also 
> select a date and time. For this demonstration you can simply click on "Today" and "Now" to select the current time
> as the time associated with the video. Click on "SAVE" to store the video.

![add_video](https://github.com/localdevices/LiveORC/assets/7658673/1b075f86-356a-45cf-8d74-dee91ae4d525)

You will return to the main video view with all your videos. There is only one now, but once you have many for many 
sites, you can use the filters on the right-hand side to only show videos of a specific site and a specific time 
range. You will also see that there is no water level associated with the video yet. A water level is always needed 
with a video before it can be processed. Click on your new video to inspect it in more detail. You can for instance
play the video if you scroll a little bit down. 

![change_video](https://github.com/localdevices/LiveORC/assets/7658673/febe7260-f8e3-43f0-ae1a-46136b29433c)

## Adding a water level to the video

Water levels are typically measured in a locally selected datum. In this example, the datum is the Dutch N.A.P. 
level, but this may also be a local staff gauge or any other logical datum. In the camera configuration, the 
relationship between the datum of water level measurements, and the datum of the vertical coordinates of ground 
control points (GCP) is already set, by defining the water level during the survey in both the local datum and the 
GCP datum. This is essential to do correctly in order to ensure LiveORC understands how to map camera coordinates 
to real-world coordinates during the video processing.

> [!NOTE]
> Under the "Assets" menu section, click on the ➕ Add button in the "Time series" menu item. Select your newly made 
> site and "Today" and "Now". Then supply the water level as 92.36. This is the water level in "Normaal Amsterdams 
> Peil" (N.A.P.) a.k.a. Amsterdam Ordnance Datum, as measured by our partner the Waterboard of Limburg. Click on 
> "SAVE" to store the water level.

![add_time-series](https://github.com/localdevices/LiveORC/assets/7658673/5c4eda98-4063-40e4-9a0b-3979303072c2)

Because you have selected "Today" and "Now" and you have selected the same site as the one you uploaded the video 
for, the water level will be automatically coupled to the video, as long as they are not too far apart. Remember 
that this was set in the "Allowed difference in time stamp" setting in the camera configuration.

## Processing your video

Now that a water level is present, we are ready to process the video. Processing occurs in a so-called asynchronous 
background process. Basically, a process is sent off to a "worker node" running NodeOpenRiverCam, which is 
continuously waiting for tasks. Once the worker node is free, it will process the task. This also means you can 
start up many tasks at the same time, and you can also have multiple workers to process tasks for you. If no worker 
is available, tasks will simply remain in the queue until a worker is free.

> [!NOTE]
> To process your video, go to the Videos menu. You will see that the RUN/STATUS now shows a Play ▶️ button
with "Click to queue". Click on it and the work will commence. On a normal PC it should take only a minute or a few 
minutes to complete. If you refresh the page (Ctrl+R), you will see the status changing from "Click to queue", to 
"Processing", and once done to "Done".

![list_video](https://github.com/localdevices/LiveORC/assets/7658673/2d69439c-3a26-4a2f-9354-6581ad373c94)

## Results

Once done, click on the Thumbnail of the video to check out the results. You can here play the video itself, and see 
a graphical interpretation of the results with the profile you have uploaded, and plots of the velocity field and 
extracted velocities over the cross-section. The text will show the water level and the median discharge also.

![change_video2](https://github.com/localdevices/LiveORC/assets/7658673/21ee03c3-f95a-4699-87d5-b0639b40c279)

You can now also go to the time series menu and see the individual time series object. You will see that it also 
contains information on the variance of the velocimetry results through 5 different quantiles (e.g. due to natural 
variability but also instabilities in the frame rate of the camera). Furthermore the fraction of the discharge that 
has been resolved optically is also shown. This is a good measure of uncertainty. OpenRiverCam uses infilling 
techniques to fill in missing velocities in the cross-section. If the fraction velocimetry value is high (e.g. 85%) 
it means that a lot of the discharge amount was actually observed optically and only a small portion (15%) comes 
from interpolated surface velocities. In the time series menu you can also export data to a preferred format using the 
EXPORT button on the top-right. This may make it easy to analyze longer series in Excel or python scripts, for instance
to update your stage-discharge relationship on the site or analyze such changes, or investigate time series behaviour.

Finally, if you go to the "Sites" menu and click on your only site so far, you will also see a time series view with 
only one red dot (water level) and one cyan dot (discharge). If you start adding more videos at different moments in 
time, this time series view will extend. If you click on a time series point, the associated video analysis will 
open, so that you can easily navigate through the results.

![change_site](https://github.com/localdevices/LiveORC/assets/7658673/aadc9718-fe88-4291-be77-937708038ac1)

## What next

Congratulations! You have now processed your first video in LiveOpenRiverCam. We hope that you have understood that 
in LiveOpenRiverCam, you can entirely organize all your videos around sites, maintain camera configurations, change 
these as you might change your set up in the field, check out time series and more. Remember that if you have many 
videos on the same site, taken with the same camera at a fixed location and orientation, you only need to add a new 
video, and a new water level, and reuse the camera configuration you've already made for your first video.

If you expect to process many videos and want to scale up, remember to look into the [Installation](#installation) 
section and in particular the section on extending the amount of [workers](#more-processing-nodes).

Of course, adding videos manually can be very useful for smaller sets, but it is also quite some work, and perhaps 
not very efficient once you want to process a lot of them. Furthermore, you may want to start setting up a field site, 
that processes on-site ("edge processing") and sends over results to your LiveORC server entirely automatically. 
LiveORC is meant to automate as much as possible so that operational use cases and services become feasible. This is 
all possible thanks to the underlying REST API of LiveORC, and the possibility to install NodeORC on an edge device 
that runs in the field. To understand how this works, please read on.

# Set up a field camera

Once you have established a camera configuration in LiveORC, you can deploy this configuration in the field, to 
process videos in the field, and only send over results. This is called "edge processing". LiveORC and NodeORC in 
combination can do this for you in a secure manner. First of all, you have to set up a camera device on your 
measurement location. The device should have a linux based operating system, and have NodeOpenRiverCam (NodeORC) 
installed. For information on how to set up NodeORC on your device, please visit
the [NodeORC](https://github.com/localdevices/nodeorc) project page. During installation, you will be able to enter 
a LiveORC server location and provide your username and password. If you do this, NodeORC can report results 
directly to LiveORC. If you have exposed LiveORC on the internet, e.g. through use of the `--hostname` and `--ssl` 
flags, you will get a connection, and the Device will appear under the `Devices` menu item in the LiveORC front end. 
This only happens if the NodeORC instance uses the same username and password as your login username and password.

The second thing needed, is that you have a camera on that site, which is configured to regularly record videos and 
store these in files that follow a template filename containing the date and time. THese files must be stored under 
the "incoming" folder, configured during installation of NodeORC. This folder is continuously monitored by the 
NodeORC instance.

Once the device has appeared in LiveORC, you can start sending camera configurations to that device. To send a task 
to a device do the following:
- go to `Camera configs`
- select your newly made camera configuration
- scroll all the way to the bottom. There you will see an option to select a device, and callbacks for video and 
  time series. The callbacks that you select will be executed every time after a video is treated.
  
![post_taskform](https://github.com/localdevices/LiveORC/assets/7658673/bb33c910-cefd-4ce7-b99d-ea036f1ba8e6)

When you click on `SEND`, the configuration will be stored under `Task forms`. If you click on `Task forms` you will 
see that the task is waiting to be picked up by the device. The device will check every 5 minutes, and before 
treating a new video, if a new task is prepared, and will validate and replace it if a new one is found. Once 
validated it will notify LiveORC that the task form is accepted. As soon as a task form is present on the NodeORC 
instance, it will start processing any video appearing in the "incoming" folder. You just have to make sure that 
camera recordings appear in the right place, and processing will then occur automatically. 

> [!IMPORTANT]
> A camera configuration MUST have a profile and a recipe attached to it, before you can send it through.
> We may expand tasks to optical water level measurements or other tasks at a later stage so that water levels can 
> be automatically estimated from a video as well.

# REST API

LiveORC has a full REST API behind the scenes. This is necessary to allow external devices and applications
to report on LiveORC. NodeORC makes ample use of the REST API for callbacks of results of video analyses, and to 
report its own status back to LiveORC. 

The REST API also allows you to develop your own applications on top of LiveORC. For instance, if you wish
to build your own web interface around OpenRiverCam for a specific user or with a specific application in 
mind this is in principle possible! The API documentation is also disclosed automatically when you start
LiveORC. If you are on `localhost:8000`, you can find it by browsing to `http://localhost:8000/api/docs`. This gives 
the documentation per API end point in Redoc format. If you prefer a Swagger layout, you can also browse to 
`http://localhost:8000/api/docs_swagger`. The api calls are available on `http://localhost:8000/api`. Replace your 
hostname by the one you have configured if necessary. We refer to this automated documentation for further reference.

# Recipes

This section describes some more information on recipes.

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
these are defined in the camera configuration for a given site. Note that the camera configuration only stores 
information that is very specific to a site, camera, the perspective that the camera sees and the coordinate system 
used to understand the geolocation and vertical datum. 

> [!TIP]
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
  default, this is set to 0.7, i.e. a minimum of 70% of the surrounding cells should have values. Typically this mask 
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

# License
LiveORC is licensed under the terms of the 
[GNU Affero General Public License v3.0](https://github.com/localdevices/LiveORC/blob/main/LICENSE)

# Trademark
See our [OpenRiverCam Trademark guidelines](https://github.com/localdevices/pyorc/blob/main/TRADEMARK.md)

