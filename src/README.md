### You can find the full documentation on ReadTheDocs [here](https://bulb.readthedocs.io/en/latest/).

---

<br/>
<br/>

# Presentation :
<br/>

![cropped and compressed logo](https://bulb.readthedocs.io/en/latest/img/cropped_and_compressed_logo.jpg)
<br/>
<br/>

The **bulb** package extends the **_Django_** framework to make it compatible with the **_Neo4j_** databases, and provides much more tools to deploy consequent websites.
Two other solutions already exist to use **Django** with **Neo4j**, but they each have their own inconveniences :  

| [**neo4django**](https://github.com/scholrly/neo4django) | [**neomodel**](https://github.com/neo4j-contrib/neomodel) |
|:--------------:|:------------:|
| This package is out of date (last update in 2013). His usage is deprecated, cause he runs under very old versions of all its components : _Python 2.X_ / _Django 1.5_ / _Neo4j 1.9_. Furthermore, **neo4django** does not provide support for the Django's sessions nor a complete support for the Django's authentication, nor a support for the Django administration. | This package is regularly updated, he runs also under last versions of all its components. He provides a very complete adaptation of the Django models, but the philosophy of these contributors is almost to make a 'ready and easy to use' tool, so the user interact only with the high-level surface. The inconvenience of a such reasoning, it's that you will have less freedom in what you want to do. This philosophy is perfect to deploy fastly some small projects, but it conduces to a total remake and to more complex programs the days where we will want to do more precise operations or we will want to improve the performances of our project, with creation of a cluster, for example. Furthermore, **neomodel** does not provides support for the Django's sessions nor for the Django's authentication and nor for the Django administration. |

**bulb** has a completely different philosophy. It offers you the choice to use "ready and easy to use" functions **to code fatser** or to let you interact with deeper concepts and to do exactly what you want to do. Firstly, the database interaction has been developed to let the user use writing queries and reading queries, but also more advanced concepts like make multi-transactions sessions and causal chaining. But on the other hand, methods have been developed to make easier the usage of these concepts.
> NB : The separation of writing and reading queries is the unique condition to set up clusters. So you you could just use these two 'ready to use' methods and get pretty good results.

Then, and to a lesser extent than **neomodel**, we have rewrite the Django's _'models'_ , to make them _'node_models'_. *bulb*'s node_models are a bit different than the original Django's models, but let you more flexibility. S

Look at this comparison chart, and make the better choice for your needs :

| | [**bulb**](https://github.com/LilianCruanes/bulb) | [**neomodel**](https://github.com/neo4j-contrib/neomodel) | [**neo4django**](https://github.com/scholrly/neo4django) |
|:--------------:|:------------:|:--------------:|:------------:|
| Python 2.X support | ❌ | ✅ | ✅ |
| Python 3.X support | ✅ | ✅ | ❌ |
| Last Neo4j versions support | ✅ | ✅ | ❌ |
| Last Django versions support | ✅ | ✅ | ❌ |
| Ready and easy to use models | ✅ | ✅ | ✅ |
| Highly customizable models | ✅ | ❌ | ❌ |
| Relationship directly integrated to models | ✅ | ✅ | ✅ |
| Independant and reusable relationship models | ✅ | ❌ | ❌ |
| Highly customizable relationship models | ✅ | ❌ | ❌ |
| Django's sessions support | ✅ | ❌ | ✅ |
| Django's authentication support | ✅ | ❌ | ✅ |
| Additional functionalities for authentication | ✅ | ❌ | ❌ |
| Django's administration support | ✅ | ❌ | ❌ |
| Highly customizable administration | ✅ | ❌ | ❌ |
| Neo4j's clusters support | ✅ | ❌ | ❌ |
| Neo4j's customizable sessions support | ✅ | ❌ | ❌ |
| Neo4j's causal chaining support | ✅ | ❌ | ❌ |
| Neo4j's geospacial operations support | ❌ | ✅ | ❌ |
| Fully CDN integration | ✅ | ❌ | ❌ |
| Automatic staticfiles compression | ✅ | ❌ | ❌ |
| Automatic staticfiles compilation | ✅ | ❌ | ❌ |
| Fully SFTP support for staticfiles | ✅ | ❌ | ❌ |
| Reinforcement of the password system | ✅ | ❌ | ❌ |
| SASS/SCSS support | ✅ | ❌ | ❌ |
| Webpack integration | ✅ | ❌ | ❌ |
| Polyfill integration | ✅ | ❌ | ❌ |
| Some front-end tools | ✅ | ❌ | ❌ |

To conclude, if you absolutely want exactly same models' structure than Django or if you have to make compatible an already existing project with Neo4j (and if you don't need neither sessions, nor authentication, nor administration), you should use [**neomodel**](https://github.com/neo4j-contrib/neomodel).
For the other cases, check this documentation :)

<br/>
<br/>
<br/>

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
> pip install bulb-core
```
or if it doesn't work :
```
> python -m pip install bulb-core
```
<br/>
<br/>

4. To check if all works, open the terminal, and go in your virtual environment if you have one. Then, run the python shell of your Django project and try to import the **bulb** package :

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

**WARNING** : don't forget to remove the default admin page at the creation of your project, cause the Django administration is'nt supported by **bulb** (**bulb** has its independent administration). Else, a "LookupError: No installed app with label 'admin'." will be raised.

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

>> The **`w_transaction()`** method, means **writing transaction**, so use it preferably when you want to create or modify datas in the database.  
We also find the **`r_transaction()`** method that means **reading transaction**, which one should be used preferably to retrieve datas from the database.
<br/>
<br/>

For now, if you have any doubt, use the **`w_transaction()`** method.
<br/>
<br/>
<br/>

---

### You can find the full documentation on ReadTheDocs [here](https://bulb.readthedocs.io/en/latest/).
