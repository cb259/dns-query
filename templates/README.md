# DNS Query Tool

## About
This tool provides a web interface to run dig commands. The commands which can be run are limited.

## Production Requirements
You will need the following to run this application in a production environment. These are additions to the Python requirements highlighted in the requirements.txt file.
* Web server such as Nginx
* WSGI such as UWSGI

## Note about running under WSGI
Running this in production under UWSGI requires the full path of DIG to be specified. For example the command line would look like this:
```
command = "/usr/bin/dig @" + nameServer + " " + host + " " + recordType
```

Failing to do this will result in a "command not found" error.