### >> Advanced Neo4j concepts :
[TOC]

<br/>

---

# Introducing
**bulb** provides easy to use functions, but it can also let the user works with the advanced Neo4j concepts handled under the hood.
These concepts are used in a Neo4j cluster organisation but are also useful for the performance of your database interactions.  
<br/>
<br/>
<br/>

---

# Databases
In a cluster organisation, your server program will have to be connected with many database servers. To create multiple and different connections, you will have to set up multiple instances of the **`Database`** class imported from **`bulb.db.base`**. As explained in all this documentation, these instances will be used to interact with each database.  
Let's see how to set up a database connection :

1) Import the **`Database`** class from **`bulb.db.base`**.  

2) Instantiate **`Database`** class to create a database connection instance. This class takes 10 parameters :  

- **`uri`** (optional): The Neo4j database uri ('bolt' or 'bolt+routing'). Explanations [here](https://neo4j.com/docs/driver-manual/1.7/client-applications/#driver-connection-uris).  
<br>
- **`id`** (optional): The Neo4j database user's id / username.  
<br>
- **`password`** (optional): The Neo4j database user's password.  
<br>
- **`encrypted`** (optional): Encrypting traffic between the Neo4j driver and the Neo4j instance. Explanations [here](https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#driver-authentication-encryption).  
<br>
- **`trust`** (optional): Verification against "man-in-the-middle" attack. Explanations [here](https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#_trust).  
   Choices :
    - 0 : TRUST_ON_FIRST_USE     (Deprecated)
    - 1 : TRUST_SIGNED_CERTIFICATES     (Deprecated)
    - 2 : TRUST_ALL_CERTIFICATES
    - 3 : TRUST_CUSTOM_CA_SIGNED_CERTIFICATES
    - 4 : TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
    - 5 : TRUST_DEFAULT = TRUST_ALL_CERTIFICATES  
<br>

These parameters define the transactions modalities (after the establishment of the initial connection. Explanations [here](https://neo4j.com/docs/api/python-driver/current/driver.html#max-connection-lifetime).  

- **`max_connection_lifetime`** (optional)  
<br>
- **`max_connection_pool_size`** (optional)  
<br>
- **`connection_acquisition_timeout`** (optional)  
<br>
- **`connection_timeout`** (optional)  
<br>
- **`max_retry_time`** (optional)  
<br/>

3) You can use this database instance to interact with the configured database.
<br/>
<br/>
<br/>

---

# Sessions
Sessions are groups of transactions used to establish an unique connection for all transactions contained in it.  
Let's see how to set up manually a session :  

1) Import the **`Session`** class from **`bulb.db.base`**.  

2) Instantiate **`Session`** class to create a session. This class takes 3 parameters :  

- **`database_instance`** (required) : You can fill it with your personalized database instance if you have one, else you can just fill it with the native **gdbh** instance imported from **`bulb.db.base`**.  
<br/>
- **`type`** (optional) : This parameter defines the access mode of the session. It can be filled with 'WRITE' or 'READ' (See more below in the **Access mode** part.)  
<br>
- **`bookmarks`** : The bookmark received by the session (See more below in the Bookmarks part).  

3) Use **with** statement to start a session environment in your program. So, you could define transactions in this environment.

<br/>
Demonstration:

```python
from bulb.db import gdbh
from bulb.db.base import Session

my_session = Session(database_instance=gdbh)

with my_session as session:
    # (define here the session's transactions)
```
<br/>
<br/>
<br/>

---

# Transactions
Transactions are sent to a Neo4j database to interact with it. As explained earlier in the documentation, transaction can be handled automatically with the **`w_transaction()`** and **`r_transaction`** of the native database instance, named **`gdbh`**. But you can also write your own transactions.
Let's see how to set up manually a transaction :

1) Import the **`Transaction`** class from **`bulb.db.base`**.  

2) Instantiate **`Transaction`** class to create a transaction. This class takes 3 parameters :  

- **`session`** (required): An instance of the above Session class.  
<br/>
- **`type`** (required): The type of the transaction ('WRITE' or 'READ'). This type, if filled, override the type of session where the transaction is contained. Explanations [here](https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-transactions-access-mode).  
 <br/>                           
- **`cypher_query`** (required): The cypher query to send to the Neo4j database.  

3) Use the **with** statement to start a transaction :

<br/>
Demonstration:

```python
from bulb.db import gdbh
from bulb.db.base import Session, Transaction

my_session = Session(database_instance=gdbh)
my_transaction = Transaction(my_session, 'WRITE', "CREATE (n:Person) RETURN (n)")

with my_session as session:
    with my_transaction as transaction:
        print('The returned value is : ', transaction)
```
<br/>
<br/>
<br/>

---

# Increase syntax
We've just shown how to set up manually transactions and sessions, but we could yet increase the syntax quality of the examples.

Demonstration :

```python
from bulb.db import gdbh
from bulb.db.base import Session, Transaction

with Session(database_instance=gdbh) as session:
    with Transaction(session, 'WRITE', "CREATE (n:Person) RETURN (n)") as transaction:
        print('The returned value is : ', transaction)
```
<br/>
<br/>
<br/>

---

# Access mode
A Neo4j cluster can be split to let a role to each database server. This role is either "READING" or "WRITING". This separation guarantees more performance and more stability in your database configuration.  
See more : [Neo4j Access Mode](https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-transactions-access-mode)  
So, the requests sent to the databases servers will have to be also oriented towards a writing database or a reading database. Here is the biggest interest to handle oneself its sessions and transactions to the Neo4j database.  
<br/>
You can define the access mode of a session : you'll have, during its instantiation, to define its **type** parameter on '**WRITE**' or '**READ**'.  
You can do the same thing with transactions, but note that if a transaction type is defined, it will override the type (if defined too) of the session in which it is contained.
See it [here](https://neo4j.com/docs/api/python-driver/current/transactions.html#access-modes).
<br/>
<br/>
<br/>

---

# Bookmarks
For more program coherence, Neo4j provides **causal chaining** with the usage of **bookmarks**. The principle is to check with a serie of bookmarks, if the requiered previous sessions have been carried out. You can learn more about it [here](https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-transactions-causal-chaining).  
<br/>
Demonstration :

```python
from bulb.db import gdbh
from bulb.db.base import Session, Transaction

saved_bookmarks = []

with Session(database_instance=gdbh) as session_1:
    with Transaction(session_1, 'WRITE', "CREATE (n:Person {name:'John'}) RETURN (n)") as transaction:
        print('The returned value is : ', transaction)
        saved_bookmarks.append(session_1.last_bookmark())
    
        
with Session(database_instance=gdbh) as session_2:
    with Transaction(session_2, 'WRITE', "CREATE (n:Person {name:'Anna'}) RETURN (n)") as transaction:
        print('The returned value is : ', transaction)
        saved_bookmarks.append(session_2.last_bookmark())

with Session(database_instance=gdbh, bookmarks=saved_bookmarks) as session_3:
    with Transaction(session_3, 'WRITE', 
    """
     MATCH (john:Person {name:'John'}),
      (anna:Person {name:'Anna'})
     CREATE (john)-[:FRIEND_WITH]->(anna)
     CREATE (anna)-[:FRIEND_WITH]->(john)
     """) as transaction:
        pass
```
<br/>
<br/>
<br/>
