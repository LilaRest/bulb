### >> Stacifiles, SFTP and CDN :
[TOC]

<br/>

---

# Introduction
Storing files in the Neo4j database isn't allowed. Some tips can allow us to do so, though files' storage is natively prohibited for a simple reason : The graph databases will slow down a lot if they have to store heavy files.

You can test it by yourself : just encode one or many heavy image(s) with the base64 algorithm and try to store it/them in your graph database. You'll observe lower performances if you run some queries.

To resolve it **bulb** provides a full static files system compatible with the Neo4j databases, with compression, management, storage and tools in order to work easily with these files.

<br/>
<br/>

# Source and content
In the following parts you'll have to distinguish the two following terms, **source files** and **content files** :
<br/>

- The **source staticfiles** are all the files (images, pdf, css, js) introduced by the developer of the website itself and that can't be changed without an update of this website.
<br/>

- The **content staticfiles** are all the files (images, pdf) introduced dynamically by the users of the website (profile picture, posted/shared pdf, etc...). A static showcase website, it won't have any **content files**.

<br/>
<br/>

# Compress and bundle the source staticfiles
**bulb** provides some tools to compress and bundle your source staticfiles (images, pdf, css, js).
Before reading the following points, make sure that your Django project is correctly configured to host staticfiles (with the **STATIC_ROOT** variable, the "static" folders, etc...).     
See : [https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/](https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/)

<br/>

## The "collectstatic" command (Django)
Before compressing the source staticfiles you have to collect them. Django provides natively the command `python manage.py collectstatic` which collects all the source staticfiles of your project in a folder named "staticfiles".

<br/>

## The "bundlestatic" command
You have just collected all your source staticfiles. **bulb** provides the command `python manage.py bundlestatic` which will compress and bundle all the previously collected staticfiles and put them into a new folder named "bundled_staticfiles".

"**Bundle**" in this case means that if a template "**article.html**" has many JS and CSS/SASS dependencies, all of them will be bundled in only two files, "**bundle_article.css**" and "**bundle_article.js**".
The bundling of the source staticfiles decreases the number of request between the client and the server a lot. Therefore, the perfomances are way more increased.

The compression also increases a lot the performances of your website and reduces a lot the cost of the files' storage.

<br/>
<br/>

# Store source staticfiles
Now that you've collected and compressed your source staticfiles you must store it somewhere.
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

> Note that **BULB_SFTP_PULL_URL** defines the url where the staticfiles can be accessed to.

<br/>

## The "pushstatic" command
**bulb** provides the `python manage.py pushstatic` command, which will send and sort your source files in your SFTP server. The command can take two parameters :
<br/>

- "**-r**" / "**--raw**" : Send the raw files (which are on the "staticfiles" folder) on the server.    
<br/>       

- "**-b**" / "**--bundled**" : Send the bundled files (which are on the "bundled_staticfiles" folder) to the server.

Per default (if no parameter is specified), both raw and bundled source files will be sent.

<br/>
<br/>

# Clear source staticfiles (the "clearstatic" command)
When you modify the source staticfiles of your project or when you create a new one, you'll have to follow again the previous step. BUT, before doing it again, you must run the `python manage.py clearstatic` command, which will remove all of the old source files on the SFTP server and purge them on the CDN (if you have configured one).
The command can take two parameters :
<br/>

- "**-r**" / "**--raw**" : Clear the raw files on the server.    
<br/>       

- "**-b**" / "**--bundled**" : Clear the bundled files on the server.

Per default (if no parameter is specified), both raw and bundled source files will be sent.

<br/>
<br/>

# The all-in-one command (the "handlestatic" command)
In the previous points we've seen :
<br/>

- The `python manage.py collectstatic` command, that collects all the source staticfiles of your project,       
<br/>   

- The `python manage.py bundlestatic` command, that bundles/compresses all the collected source staticfiles,      
<br/>  

- The `python manage.py pushstatic` command, that pushes your staticfiles on your SFTP server,       
<br/>   

- And finally the `python manage.py clearstatic` command, that clear (remove) all the old source staticfiles on the SFTP server and purge the CDN.

**bulb** provides a all-in-one command, which run these four commands : `python manage.py handlestatic`
The only thing that you've got to configure is the **BULB_SFTP_SRC_STATICFILES_MODE** settings' variable which can take three values :
<br/>   

- **"raw"** : The 'staticfiles' folder will be pushed on the sftp.      
<br/>        

- **"bundled"** : The "bundled_staticfiles" folder will be created from the 'staticfiles' folder and will be pushed on the sftp.    
<br/>   

- **"both"** : Both 'staticfiles' and 'bundled_staticfiles' folders will be pushed on the sftp.     
<br/>

Note that per default the **BULB_SFTP_SRC_STATICFILES_MODE** settings' variable is set on **"bundled"**.

So, just run this command to clear the old source staticfiles and collect, bundle, compress and push the new ones.

<br/>
<br/>

# Webpack polyfill integration

The webpack polyfill is the easiest way to implement polyfills for the entire website. Just set the **BULB_SRC_BUNDLES_USE_WEBPACK_POLYFILL** settings' variable on **True** and all your scripts will be compatible for all browsers of all versions.

But to obtain a more powerful website, it is recommended **not to use the webpack polyfill** because:
<br/>

- The webpack polyfill is directly implemented into your bundle scripts, it means that if one of your scripts doesn't need all polyfills , they'll still be loaded.     
<br/>

- The webpack polyfill doesn't have any regard on the browser used to load a page. This means that if your page is open on a modern browser which doesn't need any polyfills, they'll still be loaded.
<br/>

The best solution is to use [polyfill.io](polyfill.io) to load all the required polyfills for each different context.

A good configuration of polyfill.io is :

```html
<script crossorigin="anonymous" src="https://polyfill.io/v3/polyfill.min.js?flags=gated&features=blissfuljs%2Cdefault%2Ces2015%2Ces2016%2Ces2017%2Ces5%2Ces6%2Ces7"></script>
```

(Just implement this script tag as the first script tag of each page that could need some polyfills.)

<br/>
<br/>

# CDN integration
For this moment, **bulb** only provides support for CDN from [cdn77.com](cdn77.com)     
Feel free to contribute to the **bulb** project to make it compatible for other CDN providers.

<br/>

## CDN77

To integrate CDN77 to your project with **bulb**, just set the **BULB_USE_CDN77** settings' variable on **True** fill these three others settings' variables with your cdn77 informations :

```python
BULB_CDN77_LOGIN = "your@email.com"

BULB_CDN77_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxx"

BULB_CDN77_RESOURCE_ID = "xxxxxx"  # See : https://client.cdn77.com/support/api/version/2.0/cdn-resource#List
```

Now, the CDN will be automatically purged when files are deleted or modified on the SFTP server.

<br/>
<br/>

# Use source staticfiles
Your source staticfiles are now compressed, bundled and sorted on your SFTP server. In this part you'll see how you can use them in your project.

**bulb** provides template tags especially created to use all the source files stored on the SFTP server by an easy way.

With the native Django's staticfiles management you were using the "static" template tag to refer to your source staticfiles.

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

With **bulb** a **bulb_static** module was added, with two new template tags :
<br/>

- "**static_bundled_src**" : used to retrieve bundled source files from your SFTP server,   
<br/>

- And "**static_raw_src**" : used to retrieve raw source files from your SFTP server.
<br/>   

Note that if **DEBUG = True** the staticfiles from the "staticfiles" and "bundled_staticfiles" folders will be used.
On the other hand, if **DEBUG = False** the staticfiles from the SFTP / CDN will be used.

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

# Compress, store and use content files
As a reminder, content files are all the files introduced dynamically by the users of the website (profile picture, posted/shared pdf, etc...). A static showcase website, it won't have any **content files**.

When your SFTP server is configured, along with your CDN if you use one, you can easily use content files in your project. Just follow these steps :     
<br/>

1) Create a node model with one or many SFTP property(ies).

Example :

>> <small>node_models.py</small>
```python
from bulb.db import node_models

class Member(node_models.Node):
    username = node_models.Property(required=True)
    profile_picture = node_models.Property(sftp=True)
```
<br/>

2) Create a template with a form and a file field, and link it to a view.       
<br/>

3) Then, in the view, retrieve the file object in the **request.FILES** dict, and create the node model instance, giving this object as value of the **sftp** property.   
**bulb** will automatically compress and store the file on the SFTP server and set as concerned property value, the url through which the file can be accessed.   
<br/>

Example :

>> <small>views.py</small>
```python
from (...).node_models import Member

def registration_view(request):
    if request.POST or request.FILES:
        admin_request_post = dict(request.POST)
        admin_request_files = dict(request.FILES)
        admin_request = {**admin_request_post, **admin_request_files}

        Member.create(username=admin_request["username"],
                     profile_picture=admin_request["profile_picture"])

        (...)
```

4) Finally, just retrieve an instance of the related node_model and access to the file's url using the same way fkr every other properties.

```Python
instance.profile_picture
>>> <url>
```

<br/>
<br/>




<br/>
<br/>
<br/>
