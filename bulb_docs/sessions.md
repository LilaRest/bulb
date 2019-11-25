### >> Sessions :
[TOC]

<br/>

---

# Introduction
**bulb** provides an easy usage of Django's sessions, with the Neo4j databases. So, it'll be possible to implement login, registration portals, and logout button, to your website.
Like in the native Django' sessions, the module interacts with the **bulb** authentication. So we can store in the sessions' datas, informations about the current logged user, and then, for example, be able to allow the access to certain pages for certain group of users only.  

> Note that to setup the sessions and if we don't want to customize them, we won't work with the **bulb** sessions themself, but yet with the **bulb** authentication, that itself relies on the sessions package.

Let's see this !  
<br/>
<br/>

---

# Login
Like in the native Django packages you'll have to create a form that allows to receive datas in the view.

Then, and like in the native Django, logging in a user is composed of 2 steps :  
<br/>
<br/>
1. First; use the **`authenticate()`** method from **`bulb.contrib.auth.authentication`** to check and retrieve the user if one already exists with the same email and the password provided by the user. This method takes as parameters, the **email** and **password** retrieved.  
<br/>
2. Finally, use the **`preserve_or_login()`** method from **`bulb.contrib.auth.authentication`**.  
This methods takes two parameters :  

- The **request** (required),  
<br/>

- **`if_authentication_user`** (optional) : You have to fill this parameter in the case of an explicit authentication, like below, in a login page : where you retrieve the user from the **`authenticate()`** method. If you don't fill the parameter, the method won't try to log in the user, but only to preserve his session if there is already one. In all the other cases, the method triggers a session's cleaning.

<br/>
<br/>

To summarize, this method will :  

- try to log in the user or preserve his session, if the **`if_authentication_user`** parameter is filled,  
<br/>  

- try only to preserve the user's session if the parameter isn't filled (like in the **`bulb.contrib.auth.middleware`**, that refresh and preserve the session at each request),  
<br/>  

- clean the related sessions in the database and in the cookie, if there is neither the **`if_authentication_user`** parameter, nor a user in the request (or if datas are obsolete or damaged).  
<br/>
<br/>
Demonstration : 
<br/>

> <small>views.py</small>
```python
from django.shortcuts import redirect, render
from bulb.contrib.auth.authentication import authenticate, preserve_or_login
from my_project.my_app.forms import LoginForm
from bulb.contrib.auth.authentication import get_user_model


User = get_user_model()


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(email, password)

            if isinstance(user, User):
                preserve_or_login(request, user)
                return redirect("/blog/articles")

    return render(request, 'test_app/login.html', {'form': form})
```  
<br/>
<br/>
<br/>

---

# Registration
The registration of users is mainly the role of the authentication **bulb** module. You'll have to create a form, which, on submit, will create a user. (See [Authentication](https://bulb.readthedocs.io/en/latest/authentication/))   
But for a better experience you can add an automatic login when the users have just registered :
<br/>

> <small>views.py</small>
```python
from bulb.contrib.auth import get_user_model
from my_project.my_app.forms import RegistrationForm
from bulb.contrib.auth.authentication import preserve_or_login
from django.shortcuts import redirect, render


User = get_user_model()


def registration_view(request):
    form = RegistrationForm(request.POST or None)


    if request.POST:
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirmation_password = form.cleaned_data["confirmation_password"]

            if password == confirmation_password:
                new_user = User.create(first_name=first_name,
                                       last_name=last_name,
                                       email=email,
                                       password=password)


                # Log in automatically the user
                preserve_or_login(request, new_user)
                return redirect("/blog/articles")


    return render(request, 'test_app/registration.html', {'form': form})
```  
<br/>
<br/>
<br/>

---

# Logout
The logout is the easiest step in the sessions' management, just use the **`force_clear_user_session()`** method. This method takes only one argument, the **request**.
<br/>

> <small>views.py</small>
```python
from bulb.contrib.auth.authentication import force_clear_user_session
from django.shortcuts import redirect


def logout_view(request):
    force_clear_user_session(request)
    return redirect('/blog/login')
```  
<br/>
<br/>
<br/>

---

# Templates
Like in the native Django packages, you'll be able to interact with sessions and authentication datas in all the templates of your project.  
<br/>
<br/>

- ## Access to the logged user instance
You can use the **user** variable to access and work with the current logged user datas :

> <small>my_template.html</small>
```html
<html lang="en">

    <head>
        <title>My website</title>
        (...)
    </head>
    
    <body>
        <p>Hi {{ user.first_name }} ! Happy to see you ! </p>
    </body>
    
</html>
```
<br/>
<br/>

- ## Apply restrictions
Sometimes we'll need to allow only certain users to see a certain content.  
<br/>
As in the native Django's package, you can allow only the logged users to see a certain content. To do so, use the **user_is_logged** variable, that returns **True** if the user is logged and **False** if he isn't.  

> <small>my_template.html</small>
```html
<html lang="en">

    <head>
        <title>My website</title>
        (...)
    </head>
    
    <body>
        <h2>Member list :</h2>
        {% if user_is_logged %}
            <ul>
                (the members list)
            </ul>
            
        {% else %}
            <p>Please, log in to see the member list.</p>
            
        {% endif %}
    </body>
    
</html>
```
<br/>
<br/>

But, if you want to apply restrictions with specific permissions, you can use the **has_perm** tag from the **auth_extras** library. This is to apply on the user variable and it takes one parameter, the codename of the permission to test, and returns **True** if the user has the permission and **False** if he hasn't.  
> <small>my_template.html</small>
```html
{% load auth_extras %}

<html lang="en">

    <head>
        <title>My website</title>
        (...)
    </head>
    
    <body>
        <h2>Member list :</h2>
        {% if user|has_perm:"view_member_list" %}
            <ul>
                (the members list)
            </ul>
            
        {% else %}
            <p>You're not allowed to see the members list.</p>
            
        {% endif %}
    </body>
    
</html>
```
<br/>
<br/>
<br/>

---

# Views
So, you can do the same things in the views of your project.  
<br/>
<br/>

- ## Access to the logged user instance
For each new created session, the user instance is stored in the **`user`** attribute of the **`request`** object.  
So you could work with the logged user like this :

> <small>views.py</small>
```python
from bulb.db import gdbh
from django.shortcuts import render


def my_view(request):
    last_user_messages = gdbh.r_request("""
                                    MATCH (:User {uuid: '%s'}<-[:SENT_BY]-(m:Message)
                                    WHERE m.sending_datetime > date(2020-02-10)
                                    RETURN (m)
                                    """ % request.user.uuid)
                                    
                                    
    return render(request, 'my_template.html', {'last_user_messages': last_user_messages})
```
<br/>
<br/>

- ## Protect authentication pages
Sometimes, you want to forbid the access to the authentication pages (login and registration pages) when the user is logged. To do so you can use the **`protect_authentication_view`** decorator on your login and registration views. This decorator can take as an optional argument, the url towards which you want to redirect the user if he is already logged. Otherwise, you can directly define the **`BULB_HOME_PAGE_URL`** in your **settings.py** file.  
<br/>
> <small>views.py</small>
```python
from bulb.contrib.auth.decorators import protect_authentication_view


@protect_authentication_view()
def login_view(request):
    (...)
    
  
@protect_authentication_view()
def registration_view(request):
    (...)
```
<br/>
<br/>


- ## Apply restrictions
Some decorators have been developped to apply restrictions to our views. Their behaviours are similar to the native Django's views restrictions.  
<br/>
First, you can allow the access to a view only if the user is logged, and redirect him to the login page if he is not. To do that you can use above your views, the **`login_required`** decorator imported from **`bulb.contrib.auth.decorators`**. This decorator can take one parameter named **`login_page_url`**. This parameter must be defined with the url, to which redirect the user if he tries to access to the 'logged user only' view.  Otherwise, if the page to redirect to is the same for all of your projects, you could directly define the **`BULB_LOGIN_URL`** variable in your settings.py file. That variable contains the url of your login page.  
<br/>
> <small>views.py</small>
```python
from bulb.contrib.auth.decorators import login_required


@login_required()
def my_view(request):
    (...)
```
<br/>
<br/>

Once again, if you want to apply specifics restrictions (based on permissions) to views, you can use the **`permission_required`** decorator imported from **`bulb.contrib.auth.decorators`**. This decorator takes as arguments : the **codename** of the permission and optionally, the url to which redirect the user if he hasn't the permission required. Or else, you can directly define the BULB_HOME_PAGE_URL in your **settings.py** file.
<br/>
> <small>views.py</small>
```python
from bulb.contrib.auth.decorators import permission_required


@permission_required("view_adminitration_page")
def my_view(request):
    (...)
```
<br/>
<br/>

You can also limit the access to super users and/or to staff users.
<br/>
> <small>views.py</small>
```python
from bulb.contrib.auth.decorators import staff_only, super_user_only


@staff_only()
def my_view(request):
    (...)

@super_user_only()
def my_second_view(request):
    (...)

```
<br/>
<br/>
