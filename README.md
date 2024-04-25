# LiveORC
Web-based, professional and scalable velocimetry analysis for operational river monitoring with videos

# Installation
By far the easiest way to start working with LiveORC is to use docker and the liveorc.sh bash script bundled with 
the code. To use this script you will need a bash environment. Under most linux environments and mac OS this is  
available as is in any terminal window you may open. Under windows, you can use the script e.g. under git bash or in 
the Windows Subsystem for Linux environment (WSL).

## prerequisites


## local use

If you wish to use LiveORC on your own local network only, then the installation process is as simple as calling

```
./liveorc.sh start
```

## Installation for use on a public internet address.

For more scalable use on the internet you will have to expose the code on a public web address and ensure that 
traffic from and to the site is secure. To do this you need to acquire a domain name with any domain provider of 
your choice and ensure that the domain or a subdomain is forwarded to your IP address. It depends on your domain  
provider how to exactly do this but typically it boils down to making an 'A' record for either the entire domain or 
a subdomain and then providing your server's public IP address to the record. For instance you may have acquired a  
domain name called freewaterdata.com and now want to have a service on subdomain liveorc.freewaterdata.com. you can  
check your public IP address e.g. on whatismyip.com or (if you use a cloud provider) check the IP address with your  
provider. Let's say your IP address is `25.26.27.28`, you then make an 'A' record for subdomain 'liveorc' and point 
it to `25.26.27.28`. 

Once the domain is linked with your server's IP address you can simply use the liveorc.sh script to set everything 
up. Following the example domain name above:

```
./liveorc.sh start --hostname liveorc.freewaterdata.com --ssl
```

the `--ssl` option provides you with a Let's Encrypt certificate with automated renewal so that traffic is secured.

## Additional options for installation

### Use local storage instead of Minio S3 bucket

By default, LiveORC will make a virtualized Minio storage bucket for you, with username `admin` and password 
`password`. Any video, keyframe or thumbnail will be stored on this bucket. You can change this to use a local folder
instead by passing the keyword `file-system-storage`. This will write data to a local folder under `./media` 
(relative to the main LiveORC code folder). This is recommended only for local use.

### Debug mode

You can run LiveORC in debug mode by passing the argument `--debug` to the `liveorc.sh` start script. If you do so, 
in case anything goes wrong on rendering a page, you will receive more information about the error and the location 
in the code where this occurs. This may help to make an issue on the github page. In any circumstance, do not use 
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

