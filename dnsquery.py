from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import subprocess
import sys


app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def dnsQuery():
    if request.method == 'GET':
        # Render the main page
        return render_template('dns-query.html')
    elif request.method == 'POST':
        # Arguments to send to method
        hostname = str(request.form.get('hostname'))
        name_server = str(request.form.get('name_server'))
        record_type = str(request.form.get('record_type'))

        # Build the results
        result = resolver(hostname,name_server,record_type)

        # Render the page with the results
        return render_template('dns-query.html',result=result)

def resolver(host, nameServer, recordType):
    # Check if host is empty
    if host == "":
        return "No host provided!"

    # Check if nameServer is empty
    if nameServer == "":
        # Set default resolver
        nameServer = str("8.8.8.8")

    # Check if recordType is empty
    if recordType == "":
        # Set default record type to ANY
        recordType = str("ANY")

    # Build command to run
    command = "dig @" + nameServer + " " + host + " " + recordType

    # Run command and store results
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Return the command results
    return result.stdout.read().decode(sys.stdout.encoding)


if __name__ == '__main__':
    app.run(debug = True)# Docker on Debian - Media Server

## About
This document details setting up a Debian Linux based server to run docker. In this example we will create several containers for popular media applications as an example.

## Debian Setup
The assumption is that you have a working installation of Debian with sudo installed and a user with sudo permissions already configured. This document was written with Debian 9 (Stretch) in mind, but the process should translate to other versions with some adjustments.

## Docker CE Installation
Assuming a clean install, I have not included instructions to remove previous Docker installs. If your server has an existing docker install, you will want to remove it before proceeding.

1. Install the packages needed to allow for using HTTPS based repositories:
```
sudo apt-get install \
apt-transport-https \
ca-certificates \
curl \
gnupg2 \
software-properties-common
```

2. Install Docker's GPG key
`curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -`

3. Configure the Docker stable repository for the x86_64 platform:
```
sudo add-apt-repository \
"deb [arch=amd64] https://download.docker.com/linux/debian \
$(lsb_release -cs) \
stable"
```

4. Install Docker CE (Community Edition)
`sudo apt-get update`
`sudo apt-get install docker-ce docker-ce-cli containerd.io`

5. Verify Docker is installed and working:
`sudo docker run hello-world`

This accomplishes a few tasks:
**1. It confirms that Docker has been installed
**2. It confirms you server has the ability to connect to Docker Hub and pull down an image
**3. It confirms the ability to execute the container image

If this process is successful, you should see output similar to what is depicted below.
```
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```
## Mapping a CIFS Share
In this case the server acting as the docker host is intended to have a low footprint. In support of this, I will utilize a CIFS share hosted on an external NAS for most of the storage needs. The following sections detail how I am currently connecting to those shares and mounting them into the local directory strcture.

### Directory Strcture
My preference is to map my shares under /mnt. Typicall I create a sub-folder with the NAS device name and map the shares under the sub-folder. You can use the `sudo mkdir -p /mnt/nas_name/share1` command to accomplish this. The `-p` argument tells mkdir to create the folder strcture if it does not already exist.

### CIFS Dependancies
Since I am using CIFS on an older NAS I need to install the cifs-utils package on the server.

`sudo apt-get install cifs-utils`

### CIFS Authentication
The method I use to authenticate to the share is to utilize a text file stored in the /root directory with the needed username and password which will later be referenced in the fstab file. The following steps will create this file:
```
su
touch /root/.cifscreds
nano /root.cifscreds
```

The contents of the .cifscreds file should follow the format below:
```
username=bytecache
password=dont_tell
```

### /etc/fstab
Now we will edit the fstab file to add the new shares. First let's open the file for editing.

`sudo nano /etc/fstab`

Once we have the file open for editing I add the following as a new section in the file:
```
#CIFS Shares
//192.168.1.1/share1 /mnt/nas_name/share1      cifs    vers=1.0,credentials=/root/.cifscreds,uid=1000,gid=1000        0 0
//192.168.1.1/share2 /mnt/nas_name/share2      cifs    vers=1.0,credentials=/root/.cifscreds,uid=1000,gid=1000        0 0
```
Below is an explanation of some of the key details of the configuration above.
* The "//192.168.1.1/share1" section specifies the NAS IP and share ame
* "/mnt/nas_name/share1" reflects the local destionation where the share is to be mounted
* "vers=1.0" proves I really do have a very old NAS!
* The credentials section tells fstab where to find the credentials for authentication
* The uid and gid parameters sets the owner of the files (You can find the desired UID and GID using the `id <USER>` command)

### Mounting the Shares
With the fstab file being edited, these shares should be mounted upon boot. However to mount them without rebooting an to troubleshoot, utilize the following command:

`sudo mount -a`

## On to the Containers
We will have several containers as summarised below

* Sickrage
* NZBGet
* Deluge
* CouchPotato

### Container Creation
Below are the container creation commands for each application. Each container has some similar configuration parameters such as the Time Zone. While other has unique parameters such as configured path mappings.

#### Sickrage
```
sudo docker create --name=sickrage \
--restart unless-stopped \
-v /home/cb/sickrage/config:/config \
-v /mnt/nas_name/share1/completed:/downloads \
-v /mnt/nas_name/share1/completed/Series:/tv \
-v /mnt/nas_name/share1/Shows:/shows \
-e PGID=1000 -e PUID=1000 \
-e TZ=America/New_York \
-p 8081:8081 \
sickrage/sickrage
```

#### NZBGet
```
sudo docker create --name=nzbget \
-e PUID=1000 \
-e PGID=1000 \
-e TZ=America/New_York \
-p 6789:6789 \
-v /home/user/nzbget/config:/config \
-v /mnt/nas_name/share1:/downloads \
--restart unless-stopped \
linuxserver/nzbget
```

#### Deluge
```
sudo docker create --name=deluge \
--net=host \
-e PUID=1000 \
-e PGID=1000 \
-e TZ=America/New_York \
-v /home/user/deluge/config:/config \
-v /mnt/nas_name/share1/completed:/downloads \
--restart unless-stopped \
linuxserver/deluge
```

#### Couch Potato
```
sudo docker create \
--name=couchpotato \
-e PUID=1000 \
-e PGID=1000 \
-e TZ=America/New_York \
-p 5050:5050 \
-v /home/user/couchpotato/config:/config \
-v /mnt/nas_name/share1/completed:/downloads \
-v /mnt/nas_name/share1/Movies:/movies \
--restart unless-stopped \
linuxserver/couchpotato
```

## Running the Containers
The above configuration created the containers, however we need to start the containers in order for the applications to become functional.

```
sudo docker start sickrage
sudo docker start nzbget
sudo docker start deluge
sudo docker start couchpotato
```

## Verification & Troubleshooting

* Verify created containers and their current status - `sudo docker ps -a`
* Remove a container - `sudo docker rm <CONTAINER>`