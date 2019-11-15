### >> Conventions :  
<br/>

1. **The getter methods** that should return node, the returned value must always be :
    - Either an instance of the node corresponding class (Example : the **`get()`** method of the **`bulb.contrib.auth.node_models.User()`** node model), 
    - Or JSONified datas of the node (No example).  
    <br/>
    
    If there are multiple nodes, they will be stored in a list or a set (Example : the **`get_only_user_permissions()`** method of the **`bulb.contrib.auth.node_models.User()`** node model).
<br/>
<br/>
<br/>

2. **Permissions** should always have a codename composed by a CRUD element ("create", "view", "update", "delete") + (optional) a target + the concerned node models name or the concerned entity name, in lowercase.  
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