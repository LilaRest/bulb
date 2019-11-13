### >> Stacifiles, SFTP and CDN :
[TOC]

<br/>

---

# Introducing
Storing files in the Neo4j database is not allowed. Some tips can able us to do this, but if files storage is natively prohibited is for a simple reason : The graph databases will slow down a lot if they had to store heavy files.

You can test it by yourself : just encode one or many heavy image(s) with the base64 algorithm and try to store it/them in your graph database. You should observe lowest performances when you run some queries.

To resolve it **bulb** provides a full static files system compatible with the Neo4j databases, with compression, management, storage and tools to easily work with these files.

<br/>
<br/>

# Compress and bundle staticfiles
**bulb** provides some tools to compress and bundle your staticfiles (images, pdf, css, js).
Before to read the next points, be sure that your Django project is correctly configured to host staticfiles (with the **STATIC_ROOT** variable, the "static" folders, etc...)

<br/>
<br/>

## The "collectstatic" command (Django)
Before to compress staticfiles you have to collect them. Django provides natively the command `python manage.py collectstatic` which collects all the staticfiles of your project into a folder named "staticfiles".

<br/>
<br/>

## The "bundlestatic" command
You have just collected all your staticfiles. **bulb** provides the command `python manage.py bundlestatic` which will compress and bundle all the previously collected staticfiles and put them into a new folder named "bundled_staticfiles".

<br/>
<br/>

# Store staticfiles
Now that you have collected and compressed your staticfiles you must store them somewhere.
Bulb provides a full support for storage on SFTP/FTP servers, follow the next two steps to set it up :

1) Firstly, in the settings file set the variable **BULB_USE_SFTP** on **True**.

2) Secondly, fill the bulb SFTP settings' variables with the informations of your SFTP server and your user account :

>> <small>settings.py</small>
```python
#############
# BULB SFTP #
#############
BULB_USE_SFTP = True

BULB_SFTP_HOST = "sftp.myserver.com"

BULB_SFTP_USER = "xxxxxxxxxxxxxx"

BULB_SFTP_PASSWORD = "xxxxxxxxxxxxxx"

BULB_SFTP_HOST_SSH_KEY = "xxxxxxxxxxxxxx"

BULB_SFTP_PULL_URL = "https://pull.myserver.com"
```

> Note that **BULB_SFTP_PULL_URL** defines the url where the staticfiles can be acceded.

<br/>
<br/>

## The "pushstatic" command
**bulb** provides the `python manage.py pushstatic` command, which will send and sort your files in your SFTP server.

<br/>
<br/>

<br/>
<br/>
<br/>
