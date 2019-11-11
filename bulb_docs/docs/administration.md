### >> Administration :
[TOC]

<br/>

---

# Introducing
**bulb** provides an administration especially created to interact with neo4j databases.

<br/>
<br/>

# Setting up the administration
<br/>

The bulb's administration isn't automatically set when you implement bulb into your project.
But you can set it up with only 2 little steps :

1) Firstly, you'll have to define the administration's url via the **BULB_ADMIN_BASEPATH_NAME** settings' variable.
For example, if you defined this variable on **"my_admin"**, the administration will be accessible at _**www.mydomain.com/my_admin/**_    
Per default, **BULB_ADMIN_BASEPATH_NAME** is defined on **"admin"**.

2) Finally, go in the global **urls.py** file of your project, comment the line of the the native Django administration (if it isn't already done) and implement the **bulb**'s one like this :

>> <small>urls.py</small>
```python
# from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    # path('admin/', admin.site.urls),
    path(f"{settings.BULB_ADMIN_BASEPATH_NAME}/", include("bulb.contrib.admin.urls")),
]
```

<br/>

Now you can access to the administration via the url that you had defined with **BULB_ADMIN_BASEPATH_NAME** settings' variable

> _Note that the administration could'nt have any style, if you haven't followed the "Staticfiles" part of this documentation_

<br/>
<br/>

# Modularity
<br/>

Natively, **bulb**'s administration contains only the "Handling" part (see the Handling part of this documentation to learn more about it).
Later, it will contain also a "Statistic" part, a "Logs" part, and a "Bulb news" part.

But the administration is highly modular, you can add yours own administrations modules : for example a modules especially designed to create and edit the articles of an on-line newspaper, for the editorial team.

<br/>

Let's see how you can do this :

1) Firstly, be sure that the administration is correctly deployed, following the steps of the previous part.

2) Fill the settings' variable **BULB_ADDITIONAL_ADMIN_MODULES** with this syntax :

>> <small>settings.py</small>
```python
BULB_ADDITIONAL_ADMIN_MODULES = {
                                    "<application 1 name>": {
                                        "printed_name": "xxx",
                                        "path_name": "xxx",
                                        "home_view_url_name": "xxx"},

                                    "<application 2 name>": {
                                        "printed_name": "xxx",
                                        "path_name": "xxx",
                                        "home_view_url_name": "xxx"},

                                    "<application 3 name>": {
                                        "printed_name": "xxx",
                                        "path_name": "xxx",
                                        "home_view_url_name": "xxx"},

                                    (etc...)
                                }

```

<br/>

Demonstration :

>> <small>settings.py</small>
```python
BULB_ADDITIONAL_ADMIN_MODULES = {
                                    "editorial": {
                                        "printed_name": "Rédaction",
                                        "path_name": "redaction",
                                        "home_view_url_name": "editorial_home",
                                    },

                                    "an_other_admin_app": {
                                        "printed_name": "An other admin app",
                                        "path_name": "an_other_admin_app",
                                        "home_view_url_name": "an_other_admin_app_home"
                                    }
                                }
```
