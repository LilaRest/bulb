### >> Authentication :
[TOC]

<br/>

---

# Introducing
**bulb** provides a full Django authentication, compatible with the Neo4j databases.  
So, like in the native Django package, there is node classes : **`User`**, **`Group`** and **`Permission`**.  
Let's see more about that.  
<br/>
<br/>
<br/>

---

# Initialize native permissions
For each node models and like in the native Django authentication, it is recommended to create 4 permissions for each new node models class :

- "**create_**(class name)",  

- "**view_**(class name)",  

- "**update_**(class name)",  

- "**delete_**(class name)".  
<br/>

**bulb** provides the **`bulb-init`** command to quickly create in the database, all the native permissions for the **`User`**, **`Group`** and **`Permission`** classes.  
So, you'll just have to run : **```python manage.py bulb-init```** in your terminal.  
<br/>
<br/>
<br/>

---

# Initialize all other permissions

We have just seen how to apply all the **bulb** native permissions, so it would be nice if we could do this with all other node models classes developed in a Django project.  
**bulb** provides the **`bulb-perms`** command to quickly do that.  
So, you'll just have to run : **```python manage.py bulb-perms```** in your terminal and the CRUD permissions will be created for all your own node models (but not for the natives, which ones are created with the above **`bulb-init`** command).


<br/>
<br/>
<br/>

---

# Permissions
<br/>

 - ## Create permissions

Like in the native Django authentication, permissions are instances of a class named **`Permission`**.
We can find this class into the **`bulb.contrib.auth.node_models`** file.  
A Permission instance has 2 parameters :

- **`codename`** (required and unique) : like in the Django native authentication, the **codename** serves to identify the permissions between them. The **codename** has a **unicity** constraint and is **required**.
<br/>
<br/>
- **`description`** (required and unique) : like in the Django native authentication, the **description** is a text, generally not too long, that describes the permission.
<br/>
<br/>

So you can easily create a Permission node, by using the **`create()`** method of the **`Permission`** class :

```python
from bulb.contrib.auth.node_models import Permission


Permission.create(codename="create_post",
                  description="The user can create a post into the site.")
```

> **Note** that you will have to name parameters with this method.  
Example : **`User.create(first_name="John", ...)`** and not **`User.create("John", ...)`**.



> **Note 2** that the permission codename should always contain a CRUD element ("create", "view", "update", "delete") +  a cible (optional) + the concerned node models name or the concerned entity name, in lowercase.  
<br/>

Some examples :

- **create_user** (CRUD + **`User`** node model),  
<br/>
- **view_administration_page** (CRUD + a page of the site),  
<br/>
- **update_own_messages** (CRUD + target + **`Message`** node model),  
<br/>
- **delete_post** (CRUD + **`Post`** node model),  
<br/>
etc...  
<br/>
<br/>
<br/>

- ## Work with permissions
<br/>

> - ### Retrieve permissions
The **`Permission`** class' possesses a **`get()`** method. This method has a unique specific parameter, the **codename** of the permission to retrieve, and inherits of all others parameters of the **`Node.get()`** method (See Nodes part). It returns a **`Permission`** instance :

```python
from bulb.contrib.auth.node_models import Permission


Permission.get("can_add_post")


>>> <Permission(codename="can_add_post", description="The user can add a post into the site.")>
```

<br/>
<br/>

> - ### Update and delete permissions

Like all the node_models' instances, permissions instances possess **`update()`** and **`delete()`** methods.
<br/>
<br/>
<br/>


---

# Groups
<br/>

 - ## Create groups

Like in the native Django authentication, groups are instances of a class named **`Group`**.  
We can find this class into the **`bulb.contrib.auth.node_models`** file.  
A Group instance has 2 parameters :

- **`uuid`** (do not fill) : Each group has an Universal Unique Identifier. This parameter must not be filled in during the Group instantiation because it is automatically filled in.  
<br/>
- **`name`** (required and unique) : like in the Django native authentication, the **name** parameter is the name of the group.  
<br/>

So you can easily create a Group node, by using the **`create()`** method of the **`Group`** class :

```python
from bulb.contrib.auth.node_models import Group


Group.create(name="SuperUser")
```  

> Note that you will have to name parameters with this method.  
Example : **`User.create(first_name="John", ...)`** and not **`User.create("John", ...)`**.

<br/>
<br/>

- ## Work with groups
<br/>

> - ### Get groups

The **`Group`** class possesses a **`get()`** method. This method has a unique parameter, the **name** of the group to retrieve, and returns a **`Group`** instance :

```python
from bulb.contrib.auth.node_models import Group


Group.get("Moderator")


>>> <Group(name="Moderator", uuid="dcadfbcb4dc04bd3b8dbeb0df1e1bcd6")>

```
<br/>
<br/>

> - ### Update and delete groups
Like all the node_models, groups instances possesses **`update()`** and **`delete()`** methods.

<br/>
<br/>

> - ### Access groups' users

The **`Group`** instances possess a **`users`** property, which one allows us to access at the group-users relationship :
```python
from bulb.contrib.auth.node_models import Group


editors_group = Group.get("editors")

editors_group.users

>>> <GroupUsersRelationship object(uuid="<bulb.db.node_models.Property object at 0x7f046f642e48>")>
```
_See the part "Relationships" of this documentation to learn all what you can do with this Relationship object._

<br/>
<br/>

> - ### Access groups' permissions

The **`Group`** instances possess a **`permissions`** property, which one allows us to access at the group-permissions relationship :
```python
from bulb.contrib.auth.node_models import Group


editors_group = Group.get("editors")

editors_group.permissions

>>> <GroupPermissionsRelationship object(uuid="<bulb.db.node_models.Property object at 0x7f046f642e48>")>
```
_See the part "Relationships" of this documentation to learn all what you can do with this Relationship object._
<br/>
<br/>
<br/>

---

# Users
<br/>

 - ## Create users

Like in the native Django authentication, users are instances of a class named **`User`**.
We can find this class into the **`bulb.contrib.auth.node_models`** file.  
A User instance has 8 parameters :  

- **`uuid`** (do not fill) : Each user has an Universal Unique Identifier. This parameter must not be filled in during the User instantiation because it is automatically filled in.  
<br/>
- **`is_super_user`** (optional, default=**False**) : As in the native Django authentication, this parameter can be either True or False. If defined on True, the user possesses full rights, he can do anything.  
<br/>
- **`is_staff_user`** (optional, default=**False**) : As in the native Django authentication, this parameter can be either True or False. If defined on True, the user can access to the administration page of the site.  
<br/>
- **`is_active_user`** (optional, default=**True**) : As in the native Django authentication, this parameter can be either True or False. If defined on True, the user can log into the site. However, if defined on False, the account of the user can be considered as **"deactivated"** : the user can not log into the website.  
<br/>
- **`first_name`** (required) : The first name of the user.  
<br/>
- **`last_name`** (required) : The last name of the user.  
<br/>
- **`email`** (required) : The email of the user.  
<br/>
- **`password`** (required) : The encrypted password of the user.  
<br/>
- **`registration_datetime`** (do not fill, default=**datetime.datetime.now**) : The datetime value at the moment where the user has created this account.  This parameter must not be filled in during the User instantiation because it is automatically filled in.  
<br/>

Before users creation, 2 variables must be defined in your general **settings.py** file and below the the **`set_bulb_settings_on()`** method :  

- **`PEPPER_1`** : A string used in the password hashing to strengthen the solidity of the hash. **This string must be secret.**  
<br/>
- **`PEPPER_2`** : (The same thing).  
<br/>

Example :

>> <small>settings.py</small>
```python
PEPPER_1 = 'zwHD2UiZgk4ftvp0qxSQ'


PEPPER_2 = 'ApTIqGSLDqE2.!'
```  
<br/>

> Note that you could modify the **`_pepper()`** method in **`bulb.contrib.auth.hashers`** to add a personalized peppers management. On the other hand, you must do that before the first password savings, because the **`_pepper()`** method is also used to check passwords during authentication.  
<br/>

There are 2 classmethods to create an user, named **`create()`** and **`create_super_user()`** :  

- The **`create()`** method has the same behaviour as an instantiation of the **`User`** class, except that the raw password provided is automatically hashed before saving in the database.  
<br/>
- The **`create_super_user()`** method, creates a user, hashes the raw password before saving, but in addition to that, it forces also the **`is_super_user`** and **`is_staff_user`** parameters of the new user, to **True**.
<br/>
<br/>

**WARNING** : To create a user, **never use** the simple **instantiation** of the **`User`** class because it doesn't provide an automatic password hashing (same behaviour that the native Django authentication). Store the raw passwords in the database is a very **bad and dangerous practice**.
<br/>

> Note that you will have to name parameters with this method.  
Example : **`User.create(first_name="John", ...)`** and not **`User.create("John", ...)`**.

Demonstration :

```python
from bulb.contrib.auth.node_models import User


bob = User.create(first_name="Bob",
                  last_name="C",
                  email="bob@mail.com",
                  password="1234")


# Or to create automatically a super user :
bob = User.create_super_user(first_name="Bob",
                             last_name="C",
                             email="bob@mail.com",
                             password="1234")


# But to do the same thing, you could have done that :
bob = User.create(first_name="Bob",
                  last_name="C",
                  email="bob@mail.com",
                  password="1234",
                  is_super_user=True,
                  is_staff_user=True)


# In the other hand, this, would have raised an error :
bob = User.create_super_user(first_name="Bob",
                             last_name="C",
                             email="bob@mail.com",
                             password="1234",
                             is_super_user=False)

```  
<br/>

> NB : Like in the native Django authentication, you could use the command **`python manage.py createsuperuser`** in your terminal to create a super user. You'll only have to follow the indications.  

<br/>
<br/>



- ## Work with users  
<br/>

> - ### Get users

The **`User`** class possesses a **`get()`** method. This method has 2 parameters, the **uuid** of the user to retrieve and/or his **email**, and returns a **`User`** instance :

```python
from bulb.contrib.auth.node_models import User


User.get(email="john@mail.com")


>>> <User(first_name="John", last_name="X", uuid="a81a8d8259ab4f239c6e7b12b3a576b3")>

```
<br/>
<br/>

>  - ### Update and delete users

Like all the node_models, users instances possesses **`update()`** and **`delete()`** methods.

<br/>
<br/>

> - ### Access users' groups

The **`User`** instances possess a **`groups`** property, which one allows us to access at the user-groups relationship :
```python
from bulb.contrib.auth.node_models import User


john = User.get(email="john@mail.com")

john.groups

>>> <UserGroupsRelationship object(uuid="<bulb.db.node_models.Property object at 0x7f046f642e48>")>
```
_See the part "Relationships" of this documentation to learn all what you can do with this Relationship object._

<br/>
<br/>

> - ### Access users' permissions

The **`User`** instances possess a **`permissions`** property, which one allows us to access at the user-permissions relationship :
```python
from bulb.contrib.auth.node_models import User


john = User.get(email="john@mail.com")

john.permissions

>>> <UserPermissionsRelationship object(uuid="<bulb.db.node_models.Property object at 0x7f046f642e48>")>
```
_See the part "Relationships" of this documentation to learn all what you can do with this Relationship object._

<br/>
<br/>

> - ### Access users' sessions

The **`User`** instances possess a **`session`** property, which one allows us to access at the user-session relationship :
```python
from bulb.contrib.auth.node_models import User


john = User.get(email="john@mail.com")

john.session

>>> <UserSessionRelationsip object(uuid="<bulb.db.node_models.Property object at 0x7f046f642e48>")>
```
_See the part "Relationships" of this documentation to learn all what you can do with this Relationship object._

<br/>
<br/>

> - ### Test users' permissions

The **`User`** instances possess a **`has_perm()`** method that test if an user has a certain permission. This method has a unique parameter : the **codename** of the property to check.
```python
from bulb.contrib.auth.node_models import User


an_user = User.get(uuid="a81a8d8259ab4f239c6e7b12b3a576b3")


print(an_user.has_perm('delete_session'))


>>> False

```
<br/>
<br/>
<br/>
