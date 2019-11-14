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

# Source and content
In the following parts you'll have to make difference between **source files** and **content files** :
<br/>

- The **source staticfiles** are all the files (images, pdf, css, js) introduced by the website developer itself and that couldn't be changed without an update of the website.     
<br/>

- The **content staticfiles** are all the files (images, pdf) introduced dynamically by the users of the website (profile picture, posted/shared pdf, etc...). A static showcase website, it will not have any **content files**.
<br/>
<br/>

# Compress and bundle the source staticfiles
**bulb** provides some tools to compress and bundle your source staticfiles (images, pdf, css, js).
Before to read the next points, be sure that your Django project is correctly configured to host staticfiles (with the **STATIC_ROOT** variable, the "static" folders, etc...).     
See : [https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/](https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/)

<br/>

## The "collectstatic" command (Django)
Before to compress source staticfiles you have to collect them. Django provides natively the command `python manage.py collectstatic` which collects all the source staticfiles of your project into a folder named "staticfiles".

<br/>

## The "bundlestatic" command
You have just collected all your source staticfiles. **bulb** provides the command `python manage.py bundlestatic` which will compress and bundle all the previously collected staticfiles and put them into a new folder named "bundled_staticfiles".

"**Bundle**" in this case means that if a template "**article.html**" has many JS and CSS/SASS dependencies, all of them, will be bundled in only two file "**bundle_article.css**" and "**bundle_article.js**".
The bundling of the source staticfiles decreases a lot the number of the request between the client and the server, and so increases a lot the performances.

The compression also increases a lot the performances of your website and reduces a lot the cost of the files storage.

<br/>
<br/>

# Store source staticfiles
Now that you have collected and compressed your source staticfiles you must store them somewhere.
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

## The "pushstatic" command
**bulb** provides the `python manage.py pushstatic` command, which will send and sort your source files in your SFTP server. The command can take two parameters :
<br/>

- "**-r**" / "**--raw**" : Send the raw files (which are on the "staticfiles" folder) on the server.    
<br/>       

- "**-b**" / "**--bundled**" : Send the bundled files (which are on the "bundled_staticfiles" folder) on the server.

Per default (if no parameter is specified), both raw and bundled source files will be sent.

<br/>
<br/>

# Clear source staticfiles (the "clearstatic" command)
When you do a modification on the source staticfiles of your project or when you create new ones, you'll have to follow an other time all the preview steps. BUT, before doing them an other time, you must run the `python manage.py clearstatic` command, which will clear (remove) all the old source files on the SFTP server and purge them on the CDN (if you have configured one).
The command can take two parameters :
<br/>

- "**-r**" / "**--raw**" : Clear the raw files on the server.    
<br/>       

- "**-b**" / "**--bundled**" : Clear the bundled files on the server.

Per default (if no parameter is specified), both raw and bundled source files will be sent.

<br/>
<br/>

# The all-in-one command (the "handlestatic" command)
In the previous points we have seen :
<br/>

- The `python manage.py collectstatic` command, which collect all the source staticfiles of your project,       
<br/>   

- The `python manage.py bundlestatic` command, which bundle/compress all the collected source staticfiles,      
<br/>   

- The `python manage.py pushstatic` command, which push your staticfiles on your SFTP server,       
<br/>   

- And finally the `python manage.py clearstatic` command, which clear (remove) all the old source staticfiles on the SFTP server and purge the CDN.

**bulb** provides a all-in-one command, which one run these four commands : `python manage.py handlestatic`
Just run this command to clear the old source staticfiles and collect, bundle, compress and push the new ones.

<br/>
<br/>

# Use source staticfiles
You're source staticfiles are now compressed, bundled and sorted on your SFTP server. In this part you'll see how you can use them into your project.

**bulb** provides template tags especially created to use all the source files stored on the SFTP server by an easy way.

With the native Django's staticfiles management you used the "static" template tag to refer to your source staticfiles.

Example :

```html
(...)

{% load static %}

<head>
    <link rel="stylesheet" href="{% static "archives/css/style/article_small_page.css" %}"/>
    <link rel="stylesheet" href="{% static "archives/css/style/article_medium_page.css" %}"/>
    <link rel="stylesheet" href="{% static "archives/css/style/article_large_page.css" %}"/>
</head>

(...)
```

With **bulb** a **bulb_static** module was added with two new template tags :
<br/>

- "**static_bundled_src**" : used to retrieve bundled source files from your SFTP server,
<br/>

- And "**static_raw_src**" : used to retrieve raw source files from your SFTP server.
<br/>

Example :

```html
(...)

{% load static bulb_static %}

<head>
    {% if DEBUG %}
        <link rel="stylesheet" href="{% static "archives/css/style/article_small_page.css" %}"/>
        <link rel="stylesheet" href="{% static "archives/css/style/article_medium_page.css" %}"/>
        <link rel="stylesheet" href="{% static "archives/css/style/article_large_page.css" %}"/>

    {% elif not DEBUG %}
        <link rel="stylesheet" href="{% static_bundled_src 'archives/bundle_article.css' %}"/>

    {% endif %}
</head>

(...)
```
<br/>
<br/>


<br/>
<br/>
<br/>
