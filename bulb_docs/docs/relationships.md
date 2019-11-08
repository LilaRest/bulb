### >> Relationships :
[TOC]

<br/>
<br/>

---

# Introducing
**bulb** provides a group of classes used to structure and manipulate relationships and properties.  
Only the most important things have been introduced, in order to leave lots of flexibility to the package's user and not to burden him with useless things.  
Furthermore, when you work with a database, personalization of each request is the key of fast and powerful interactions. So don't hesitate to make your own request, for complexes works.
<br/>
<br/>
<br/>

---

# Relationships models  
> Note that all **relationships models** in each application, must be written in files named **`node_models.py`**.  

<br/>

The Relationship instances, possesses some parameters which define their behaviour in the database :

- **`rel_type`** (required) : This parameter defines the relationship type. It must be a string.    
                              See : [https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-relationship-types](https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-relationship-types)   
<br/>
- **`direction`** (optional, default="from") : Must be "from", "to", or "bi". If it is "from", the relationship will be an arrow that starts from the self node_model's instance to other node_models' instances. If it is "to" it will be the reverse case : the relationship will be an arrow that starts from other node_models' instances to the self node_model's instance.Finally if it is "bi", it will be two relationships that will work by peers, one from and one to the self node_model's instance : a bi-directional relationships will be created.   
<br/>
- **`properties_fields`** (optional, default=None) : A dict of properties for "all in node_model" syntax. If the Relationship classes are out of the node_model classes, this argument will be None.
<br/>
- **`start`** (optional, default=None) : This parameter must be a node_model class, its name or "self". It applies a start constraint to the relationship.    
<br/>                          
- **`target`** (optional, default=None) : This parameter must be a node_model class, its name or "self". It applies a target constraint to the relationship.  
<br/>
- **`auto`** (optional, default=False) : This parameter must be a boolean. If it is True, the relationship is allowed to be applied on one unique node, which one will be the start and the target of the relationship.   
<br/>
- **`on_delete`** (optional, default="PROTECT") : This parameter must be "PROTECT" or "CASCADE". It defines the behavior of the related nodes. If it is "PROTECT", if the self node object of the relationship is deleted, nothing happen for nodes related to it (A simple DETACH DELETE command is run). In the other hand, if it is "CASCADE", the other nodes will be deleted in the same time as the self node object.    
<br/>
- **`unique`** (optional, default=False) : This parameter must be a boolean. If it is True the relationship will be unique.    


<br/>

- ## Implement relationships models

There are **two different syntaxes** to implement relationships into your project, but both are using the **`Relationship`** class imported from **`bulb.db.node_models`**.

Let's see the two different ways to use relationships :
<br/>
<br/>

>- ### The "all in node_models" syntax

With this syntax, you can define the Relationship as an attribute of a node_model. Useful and convenient if you don't have to reuse the relationship configuration for another node_model.

>> <small>node_models.py</small>
```python
from bulb.db import node_models
import datetime


class Article(node_models.Node):
    title = node_models.Property(required=True,
                                 unique=True)
    content = node_models.Property(required=True)
    publication_datetime = node_models.Property(default=datetime.datetime.now)
    authors = node_models.Relationship(rel_type="WROTE",
                                       direction="to",
                                       start="User",
                                       target="self",
                                       on_delete="CASCADE")

```

<br/>

>- ### The "distinct" syntax

With this syntax, you can define a Relationship model and reuse it for multiple cases.

>> <small>node_models.py</small>
```python
from bulb.db import node_models
import datetime

class RelatedAuthorsRelationship(node_models.Relationship):
    rel_type = "WROTE"
    direction = "to"
    start = "User"
    target = "self"
    on_delete = "CASCADE"


class Article(node_models.Node):
    title = node_models.Property(required=True,
                                 unique=True)
    content = node_models.Property(required=True)
    publication_datetime = node_models.Property(default=datetime.datetime.now)
    authors = RelatedAuthorsRelationship()


class Comment(node_models.Node):
    content = node_models.Property(required=True)
    author = RelatedAuthorsRelationship(unique=True)

```

<br/>
<br/>

- ## Access to the relationships instances

When the previous step is done, you could now access to the Relationship instances through the related node attribute.

See this example (based on the previous examples) :

>> <small>node_models.py</small>
```python
(...)

>>> my_article = Article.get(uuid="872a5f767485486a853e5d2886850fa2")
>>> my_article.authors
<RelatedAuthorsRelationship object(uuid="f37a4ae83e994aa8812b42de52c11b70")>

```

These instances will able you to work with the relationships.

<br/>
<br/>

- ## Create relationships

Create the relationship is the easiest step cause all the configuration and behaviours have been defined in the previous step.
To do this you only have to use the **`add()`** method of instances of the **`Relationship`** class.

This method can take 3 parameters :

- **`instance`** (required if not uuid) : A node_model's instance, to which the relationship will target.  
<br/>
- **`uuid`** (required if not instance) : A node_models uuid, to which the relationship will target.   
<br/>
- **`properties`** (optional) : The properties dictionary to fill if the relationship take one or more properties.     


Remember that in the previous example we had defined the **`RelatedAuthorsRelationship`** and see this demonstration :

>> <small>node_models.py</small>
```python
from bulb.db import node_models
from bulb.contrib.auth.node_models import User
import datetime

class RelatedAuthorsRelationship(node_models.Relationship):
    rel_type = "WROTE"
    direction = "to"
    start = "User"
    target = "self"
    on_delete = "CASCADE"


class Article(node_models.Node):
    title = node_models.Property(required=True,
                                 unique=True)
    content = node_models.Property(required=True)
    publication_datetime = node_models.Property(default=datetime.datetime.now)
    authors = RelatedAuthorsRelationship()

first_article = Article.create(title="A great article !",
                               content="Lorem ipsum...")

john = User.get(email="john@mail.com")

# Add john as author of the first article
first_article.authors.add(john)

```

<br/>
<br/>

- ## Work with Relationship instances
<br/>

> - ### Retrieve relationships elements

A relationship is composed by two nodes and the relationship that joins them.
The relationships possesses a **`get()`** method. This method allows us to retrieve one/two node(s) of a relationship and/or the relationship object. As the get() method of the node_models, this one takes many parameters to able us to do very complex and customizable requests :

- **`direction`** (optional, default="bi") : Must be "from", "to", or "bi". If it is "from", the research will be focused on all the relationships that have as start point the self node_model's instance. If it is "to", the research will be focused on all the relationships that have as end point the self node_model's instance. Finally, if it is "bi", the research will be focused on the relationships of both cases.   
<br/>
- **`returned`** (optional, default="node") : Must be "rel", "node" or "both". If it is "rel", the method will return a list that contains relationships as RelationshipInstance (or of one of its children classes) instances. If it is "node", the method will return a list that contains the nodes at the other ends of these relationships as node_models' instances. Finally if it is "both", it will return a list of dictionaries in which ones the "rel" key refers to a relationships and the "node" key to its associated node.   
Example :          
```python
{"rel": <RelationshipInstance object(uuid="3a43238c76ec4d6cb392b138f0871e75")>,
"node": <Human object(uuid="ec04770e5c8b428d9d94678c3666d312")>}
```     
<br/>

- **`order_by`** (optional, default=None) : Must be the name of the property with which the returned datas will be sorted. BUT, if self.returned = "both", two different types of datas will be returned (relationships and nodes). So to sort them this property must start with "r." (like 'relationships') or "n." (like 'nodes').       
 Examples : "r.datetime", "n.first_name", etc...      
<br/>
- **`limit`** (optional, default=None) : Must be an integer. This parameter defines the number of returned elements.   
<br/>
- **`skip`** (optional, default=None) : Must be an integer. This parameter defines the number of skipped elements. For example if self.skip = 3, the 3 first returned elements will be skipped.    
<br/>
- **`desc`** (optional, default=False): Must be a boolean. If it is False the elements will be returned in an increasing order, but it is True, they will be returned in a descending order.   
<br/>
- **`distinct`** (optional, default=False) : Must be a boolean. If it is True, the returned list will be only composed with unique elements.    
<br/>
- **`only`** (optional, default=None) : Must be a list of field_names. If this parameter is filled, the return will not be node_models and relationships instances, but a dict with "only" the mentioned fields. BUT, if self.returned = "both", two different types of datas will be returned (relationships and nodes). So to mention their properties fields, the elements of the list will must start with "r." (like 'relationships') or "n." (like 'nodes').     
 Examples : "r.datetime", "n.first_name", etc...    
 <br/>
 - **`filter`** (optional, default=None) : Must be Q statement. You must use the Q class stored in bulb.db  
 Example: Q(name__contains="al") | Q(age__year__lte=8)   
 <br/>
- **`return_query`** (optional, default=False) : Must be a boolean. If true, the method will only return the cypher query.   

Remember that in the previous example we had defined the **`RelatedAuthorsRelationship`** and see this demonstration :

>> <small>node_models.py</small>
```python
from bulb.db import node_models
from bulb.contrib.auth.node_models import User
import datetime

class RelatedAuthorsRelationship(node_models.Relationship):
    rel_type = "WROTE"
    direction = "to"
    start = "User"
    target = "self"
    on_delete = "CASCADE"


class Article(node_models.Node):
    title = node_models.Property(required=True,
                                 unique=True)
    content = node_models.Property(required=True)
    publication_datetime = node_models.Property(default=datetime.datetime.now)
    authors = RelatedAuthorsRelationship()

first_article = Article.create(title="A great article !",
                               content="Lorem ipsum...")

john = User.get(email="john@mail.com")

# Add john as author of the first article
first_article.authors.add(john)

# Retrieve nodes from the other side of the relationship :
first_article.authors.get()
>>> [<User object(first_name="John", last_name="Doe", uuid="20b4ab050cb141868c8cd39dad4d9db2")>]

# Also return the relationships :
first_article.authors.get(returned="both")
>>> [{'rel': <RelatedAuthorsRelationshipInstance object(uuid="db087a94fda54427bf3ef52de425e301")>, 'node': <User object(first_name="John", last_name="Doe", uuid="20b4ab050cb141868c8cd39dad4d9db2")>}]

```

<br/>
<br/>

> - ### Make your own getter, setter and deletter

A Relationship instance possesses native getter, setter and deletter, but these methods could be personalized for each Relationship class. Handle perfectly all the situations is impossible, and try to do this, leads to very heavy and inefficient programs. To make your own node methods, you'll just have to take the native methods and re-implement them with your modifications.

<br/>
<br/>

- ## Work with RelationshipInstance instances
<br/>
We have just seen how to work with **`Relationship`** instances. As a reminder, the **`Relationship`** class allow us to create relationships models and then create relationships in the database which ones respects these models.
But you have to know that an other class exists to represent the relationships themselves in the database, it is called **`RelationshipInstance`**.
For example, if you use the **`get()`** method of the **`Relationship`** instances, you can retrieve both nodes and relationships by settings **returned** parameter on **'both'**.     
Let's see a demonstration which is based on the example of the  **`get()`** method of the **`Relationship`** instances (above) :

>> <small>node_models.py</small>
```python
from bulb.db import node_models
from bulb.contrib.auth.node_models import User
import datetime

class RelatedAuthorsRelationship(node_models.Relationship):
    rel_type = "WROTE"
    direction = "to"
    start = "User"
    target = "self"
    on_delete = "CASCADE"


class Article(node_models.Node):
    title = node_models.Property(required=True,
                                 unique=True)
    content = node_models.Property(required=True)
    publication_datetime = node_models.Property(default=datetime.datetime.now)
    authors = RelatedAuthorsRelationship()

first_article = Article.create(title="A great article !",
                               content="Lorem ipsum...")

john = User.get(email="john@mail.com")

# Add john as author of the first article
first_article.authors.add(john)

# Retrieve nodes and relationships
first_article.authors.get(returned="both")
>>> [{'rel': <RelatedAuthorsRelationshipInstance object(uuid="db087a94fda54427bf3ef52de425e301")>, 'node': <User object(first_name="John", last_name="Doe", uuid="20b4ab050cb141868c8cd39dad4d9db2")>}]
```

You can see a **`RelatedAuthorsRelationshipInstance`** instance. The **`RelatedAuthorsRelationshipInstance`** class inherits from the **`RelationshipInstance`** class.
Indeed, **bulb** automatically create children of the **`RelationshipInstance`** class based on your relationships models (classes that inherits from the **`Relationship`** class).
And if you use the "all in node_models" syntax, the **`RelationshipInstance`** class will be used.

<br/>
<br/>

> - ### Update relationships' properties

<br/>

Now you have retrieved a **`RelatedAuthorsRelationshipInstance`** instance you can update properties of the relationship that it represents. To do this, **bulb** give you an **`update()`** method. This method works identically like the **`update()`** method of the **`Node`** instances : it takes as first argument the name of the property to update and as second argument, the new value of this property.

>> <small>node_models.py</small>
```python
(...)
import datetime

my_rel_instance.update("creation_datetime", datetime.datetime.now())
```

<br/>

> - ### Delete relationships

**`RelatedAuthorsRelationshipInstance`** instances possess a **`delete()`** method, which one delete allows us to delete the relationship.

<br/>
<br/>
<br/>
