# LiveORC
Web-based, professional and scalable velocimetry analysis for operational river monitoring with videos

# Installation
By far the easiest way to start working with LiveORC is to use docker and the liveorc.sh bash script bundled with the code. To use this script you will need a bash environment. Under most linux environments and mac OS this is available as is in any terminal window you may open. Under windows, you can use the script e.g. under git bash or in the Windows Subsystem for Linux environment (WSL).

## prerequisites


## local use

If you wish to use LiveORC on your own local network only, then the installation process is as simple as calling

```
./liveorc.sh start
```

## Installation for use on a public internet address.

For more scalable use on the internet you will have to expose the code on a public web address and ensure that traffic from and to the site is secure. To do this you need to acquire a domain name with any domain provider of your choice and ensure that the domain or a subdomain is forwarded to your IP address. It depends on your domain provider how to exactly do this but typically it boils down to making an 'A' record for either the entire domain or a subdomain and then providing your server's public IP address to the record. For instance you may have acquired a domain name called freewaterdata.com and now want to have a service on subdomain liveorc.freewaterdata.com. you can check your public IP address e.g. on whatismyip.com or (if you use a cloud provider) check the IP address with your provider. Let's say your IP address is `25.26.27.28`, you then make an 'A' record for subdomain 'liveorc' and point it to `25.26.27.28`. 

Once the domain is linked with your server's IP address you can simply use the liveorc.sh script to set everything up.


