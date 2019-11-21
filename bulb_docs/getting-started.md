### >> Getting started :
[TOC]

<br/>

---

# Introduction

The **bulb package**'s setup is very fast. Only **2 steps** are required to execute your first cypher's requests.

>> If you haven't installed the package yet, please see the [installation](https://bulb.readthedocs.io/en/latest/installation/) page.  
<br/>
<br/>


# 1. Set the bulb settings to your project 

A very simple step, just import the **`set_bulb_settings_on()`** in the settings.py file of your Django project :

> <small>_settings.py_</small>
```python
from bulb import set_bulb_settings_on
```
<br/>
<br/>

Then, use this method on all the datas contained in your settings.py file. The **`locals()`** function returns a dictionary which contains all of these datas.
IIIIIIT So just put this **at the bottom** of your settings.py file :

> <small>_settings.py_</small>
```python
set_bulb_settings_on(locals())
```
<br/>
<br/>

Finally, still in the same file (**just below the method** we've set previously), configure your Neo4j credentials with theses 3 parameters :  
    - **`BULB_DATABASE_URI`**,  
    - **`BULB_DATABASE_ID`**,  
    - **`BULB_DATABASE_PASSWORD`**.

**`BULB_DATABASE_URI`** is the bolt address of your database. Usually on a local server, the bolt address is '**bolt://localhost:7687**'. You can find more details in the parameters of your Neo4j database and on the official [documentation](https://neo4j.com/docs/driver-manual/1.7/client-applications/#driver-connection-uris).

**`BULB_DATABASE_ID`** is your Neo4j database **id** or **username**. By default the id is defined on 'neo4j'.

**`BULB_DATABASE_PASSWORD`** is your Neo4j database **password**. By default the password is defined on 'neo4j' too. Usually, especially if you haven't changed the password during the first run og the Neo4j database, you'll be asked to replace the default password with one of your own. 
VIEEEEUX : But normally and if you don't have change the password before, during the first run of the Neo4j database, we will ask you to replace the default password by another. 

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

**WARNING** : don't forget to remove the default admin page at the creation of your project. Indeed, Django's administration is'nt supported by **bulb** (**bulb** has its own independent administration). Otherwise, a "LookupError: No installed app with label 'admin'." will be raised.

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


# 2. Run a first cypher query

**bulb** can be used in each of your project's file. To do so, in one of these files, import the **`gdbh`** object.

> <small>views.py</small>
```python
from bulb.db import gdbh
```
<br/>
<br/>

**g-db-h** means **_Graph Database Handler_** and it's an instance of the **`GraphDatabaseHandler()`** class. This instance will be used each time you want to interact with the Neo4j database.
<br/>
<br/>

Now you can use the **`w_transaction()`** method of the **`gdbh`** object, to send a query to the database :

```python
gdbh.w_transaction("CREATE (:Person) {first_name: 'Adrien', age: 18}")
```
<br/>

>> The **`w_transaction()`** method, means **writing transaction**, so use it preferably when you want to create or modify datas in the database.  
We also find the **`r_transaction()`** method that means **reading transaction**, which should be used preferably to retrieve datas from the database.
<br/>
<br/>

For now, if you have any doubt, use the **`w_transaction()`** method.
