(bulb is the child of the old 'neo4j_for_django' package.)

### You can find the full documentation on ReadTheDocs [here](https://bulb.readthedocs.io/en/latest/).

---

<br/>
<br/>

# Presentation :
<br/>

![transparent logo bulb](https://bulb.readthedocs.io/en/latest/img/transparent_logo_bulb.png)
<br/>
<br/>

The **bulb** package extends the **_Django_** framework to make it compatible with the **_Neo4j_** databases. But it also provides an advanced support for modern technologies (CDNs, SFTP servers, ...) and a lot of tools for better user experience and performances (a full administration crafted on graph databases' logic, staticfiles compression, ...).

---

# Installation :
<br/>

1. First, open a terminal.
<br/>
<br/>

2. Then, go into your Django project or start your virtual environment if you have one :

    Example :
```
> cd my_projects/my_django_project
```
<br/>
<br/>

3. Finally, execute :
```
> pip install bulb
```
or if it doesn't work :
```
> python -m pip install bulb
```
<br/>
<br/>

4. To check if all works open the terminal, and go in your virtual environment if you have one. Then, run the python shell of your Django project and try to import the **bulb** package :

```
(my_env) > python manage.py shell
Python 3.7.1 (v3.7.1:260ec2c36a, Oct 20 2018, 14:57:15) [MSC v.1915 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> import bulb
>>>
```

   If no error message is raised, that's good.  
<br/>
<br/>
<br/>

---

# Getting started :
<br/>

## Introducing

The **bulb package** is very fast to setup. Just **2 steps** are needed to execute yours first cypher requests.

>> If you don't have already install the package, please see the [installation](https://bulb.readthedocs.io/en/latest/installation/) page.  
<br/>
<br/>


## 1. Set the bulb settings to your project 

A very simple step, just import the **`set_bulb_settings_on()`** in the settings.py file of your Django project :

> <small>_settings.py_</small>
```python
from bulb import set_bulb_settings_on
```
<br/>
<br/>

Then, use this method on all the datas contained in your settings.py file. The **`locals()`** function return a dictionary that contains all of these datas.
So just put this **at the bottom** of your settings.py file :

> <small>_settings.py_</small>
```python
set_bulb_settings_on(locals())
```
<br/>
<br/>

Finally, and always in the same file (**just below the method** that we have previously set), configure yours Neo4j credentials with the 3 parameters :  
    - **`BULB_DATABASE_URI`**,  
    - **`BULB_DATABASE_ID`**,  
    - and **`BULB_DATABASE_PASSWORD`**.

**`BULB_DATABASE_URI`** is the bolt address of your database. Generally on a local server, the bolt address is '**bolt://localhost:7687**'. But you can find more details in the parameters of your Neo4j database and on the official [documentation](https://neo4j.com/docs/driver-manual/1.7/client-applications/#driver-connection-uris).

**`BULB_DATABASE_ID`** is your Neo4j database **id** or **username**. By default the id is defined on 'neo4j'.

**`BULB_DATABASE_PASSWORD`** is your Neo4j database **password**. By default the password is defined on 'neo4j' too. But normally and if you don't have change the password before, during the first run of the Neo4j database, we will ask you to replace the default password by another. 

Example :

> <small>_settings.py_</small>
```python
BULB_DATABASE_URI = "bolt://localhost:7687"

BULB_DATABASE_ID = 'neo4j'

BULB_DATABASE_PASSWORD = '1234'
```
<br/>

##### **You're project is now configured to work with `bulb` !**

<br/>
<br/>

**WARNING** : don't forget to remove the default admin page at the creation of your project, cause the Django administration is'nt already supported by **bulb**. Else, a "LookupError: No installed app with label 'admin'." will be raised.

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('blog/', include("my_project.urls"))
]
```
<br/>
<br/>


## 2. Run a first cypher query

**bulb** can be used in all the files of your project. So in one of these files, import the **`gdbh`** object.

> <small>views.py</small>
```python
from bulb.db import gdbh
```
<br/>
<br/>

**g-db-h** means **_Graph Database Handler_** and it is an instance of the **`GraphDatabaseHandler()`** class. This instance will be used all the times where we will want to interact with the Neo4j database.
<br/>
<br/>

Now you can use the **`w_transaction()`** method of the **`gdbh`** object, to send a query to the database :

```python
gdbh.w_transaction("CREATE (:Person) {first_name: 'Adrien', age: 18}")
```
<br/>

>> The **`w_transaction()`** means **writing transaction**, so use it preferably when you want to create or modify datas in the database.  
We also find the **`r_transaction()`** method, which one should be used preferably to retrieve datas from the database.
<br/>
<br/>

For now, if you have any doubt, use the **`w_transaction()`** method.
<br/>
<br/>
<br/>

---

### You can find the full documentation on ReadTheDocs [here](https://bulb.readthedocs.io/en/latest/).
