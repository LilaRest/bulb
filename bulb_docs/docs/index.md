# Welcome to the `bulb` documentation !
<br/>
![transparent logo bulb](img/bulb_logo.jpg)
<br/>
<br/>

---

Neo4j integration for Django, and much more tools to deploy consequent websites...
###### [**Show the project on GitHub**](https://github.com/LilianCruanes/bulb)

---

### Documentation tree :


- [Presentation](https://bulb.readthedocs.io/en/latest/presentation/)
<br/>
<br/>

- [Installation](https://bulb.readthedocs.io/en/latest/installation/)
<br/>
<br/>

- [Getting started](https://bulb.readthedocs.io/en/latest/getting-started/)
    - [Introducing](https://bulb.readthedocs.io/en/latest/getting-started/#introducing)
    - [1. Set the neo4j_for_fjango settings to your project](https://bulb.readthedocs.io/en/latest/getting-started/#1-set-the-bulb-settings-to-your-project)
    - [2. Run a first cypher query](https://bulb.readthedocs.io/en/latest/getting-started/#2-run-a-first-cypher-query)
<br/>
<br/>

- [Nodes](https://bulb.readthedocs.io/en/latest/nodes/)
    - [Introducing](https://bulb.readthedocs.io/en/latest/nodes/#introducing)
    - [Node models](https://bulb.readthedocs.io/en/latest/nodes/#node-models)
        - [Create node models](https://bulb.readthedocs.io/en/latest/nodes/#create-node-models)
        - [Work with node models](https://bulb.readthedocs.io/en/latest/nodes/#work-with-node-models)
    - [Labels](https://bulb.readthedocs.io/en/latest/nodes/#labels)
        - [Create labels](https://bulb.readthedocs.io/en/latest/nodes/#create-labels)
        - [Work with labels](https://bulb.readthedocs.io/en/latest/nodes/#work-with-labels)
    - [Properties](https://bulb.readthedocs.io/en/latest/nodes/#properties)
        - [Create properties](https://bulb.readthedocs.io/en/latest/nodes/#create-properties)
        - [Apply properties' restrictions](https://bulb.readthedocs.io/en/latest/nodes/#apply-properties-restrictions)
        - [Work with properties](https://bulb.readthedocs.io/en/latest/nodes/#work-with-properties)
    - [Methods](https://bulb.readthedocs.io/en/latest/nodes/#methods)
<br/>
<br/>

- [Authentication](https://bulb.readthedocs.io/en/latest/authentication/)
    - [Introducing](https://bulb.readthedocs.io/en/latest/authentication/#introducing)
    - [Initialize native permissions](https://bulb.readthedocs.io/en/latest/authentication/#initialize-native-permissions)
    - [Initialize all other permissions](https://bulb.readthedocs.io/en/latest/authentication/#initialize-all-other-permissions)
    - [Permissions](https://bulb.readthedocs.io/en/latest/authentication/#permissions)
        - [Create permissions](https://bulb.readthedocs.io/en/latest/authentication/#create-permissions)
        - [Work with permissions](https://bulb.readthedocs.io/en/latest/authentication/#work-with-permissions)
    - [Groups](https://bulb.readthedocs.io/en/latest/authentication/#groups)
        - [Create groups](https://bulb.readthedocs.io/en/latest/authentication/#create-groups)
        - [Work with groups](https://bulb.readthedocs.io/en/latest/authentication/#work-with-groups)
    - [Users](https://bulb.readthedocs.io/en/latest/authentication/#users)
        - [Create users](https://bulb.readthedocs.io/en/latest/authentication/#create-users)
        - [Work with users](https://bulb.readthedocs.io/en/latest/authentication/#work-with-users)
<br/>
<br/>

- [Sessions](https://bulb.readthedocs.io/en/latest/sessions/)
    - [Introducing](https://bulb.readthedocs.io/en/latest/sessions/#introducing)
    - [Login](https://bulb.readthedocs.io/en/latest/sessions/#login)
    - [Registration](https://bulb.readthedocs.io/en/latest/sessions/#registration)
    - [Logout](https://bulb.readthedocs.io/en/latest/sessions/#logout)
    - [Templates](https://bulb.readthedocs.io/en/latest/sessions/#templates)
        - [Access to the logged user instance](https://bulb.readthedocs.io/en/latest/sessions/#access-to-the-logged-user-instance)
        - [Apply restrictions](https://bulb.readthedocs.io/en/latest/sessions/#apply-restrictions)
    - [Views](https://bulb.readthedocs.io/en/latest/sessions/#views)
        - [Access to the logged user instance](https://bulb.readthedocs.io/en/latest/sessions/#access-to-the-logged-user-instance_1)
        - [Protect authentication pages](https://bulb.readthedocs.io/en/latest/sessions/#protect-authentication-pages)
        - [Apply restrictions](https://bulb.readthedocs.io/en/latest/sessions/#apply-restrictions_1)
<br/>
<br/>

- [Advanced Neo4j concepts](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/)
    - [Introducing](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/#introducing)
    - [Databases](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/#databases)
    - [Sessions](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/#sessions)
    - [Transactions](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/#transactions)
    - [Increase syntax](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/#increase-syntax)
    - [Access mode](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/#access-mode)
    - [Bookmarks](https://bulb.readthedocs.io/en/latest/advanced-neo4j-concepts/#bookmarks)
<br/>
<br/>

- [Settings](https://bulb.readthedocs.io/en/latest/settings/)
<br/>
<br/>

- [Conventions](https://bulb.readthedocs.io/en/latest/conventions/)
<br/>
<br/>

- [License](https://bulb.readthedocs.io/en/latest/license/)
<br/>
<br/>
<br/>

---

### Project tree :
<br/>

##### Administration (bulb.contrib.admin) :
- _bulb.contrib.admin._**static**/

    - _bulb.contrib.admin.static._**admin**/

        - (bulb's administration's staticfiles)
        <br/>

- _bulb.contrib.admin._**templates**/

    - _bulb.contrib.admin.templates._**admin**/

        - (bulb's administration's templates)
        <br/>

- _bulb.contrib.admin._**templatetags**/

    - **admin_extras.py**
    <br/>

- **context_processors.py**

- **forms.py**

- **node_models.py**

- **urls.py**

- **views.py**
<br/>
<br/>
<br/>


##### Authentication (bulb.contrib.auth) :
- _bulb.contrib.auth._**management**/

	- _bulb.contrib.auth.management._**commands**/

		- **bulb-init.py**

		- **bulb-perms.py**  

		- **createsuperuser.py**
		<br/>

- _bulb.contrib.auth._**templatetags**/

	- **auth_extras.py**  
	<br/>

- **authentication.py**

- **context_processors.py**

- **decorators.py**

- **exceptions.py**

- **hashers.py**

- **middleware.py**

- **node_models.py**

- **node_models_admin.py**

- **views.py**
<br/>
<br/>
<br/>


##### Handling (bulb.contrib.handling) :
- _bulb.contrib.handling._**static**/

    - _bulb.contrib.handling.static._**handling**/

        - (bulb's handler's staticfiles)
        <br/>

- _bulb.contrib.handling._**templates**/

    - _bulb.contrib.handling.templates._**handling**/

        - (bulb's handler's templates)
        <br/>

- **context_processors.py**

- **exceptions.py**

- **forms.py**

- **middleware.py**

- **node_models.py**

- **node_models_admin.py**

- **urls.py**

- **views.py**
<br/>
<br/>
<br/>


##### Sessions (bulb.contrib.sessions) :
- _bulb.contrib.sessions._**backends**/

	- **db.py**  
	<br/>

- _bulb.contrib.sessions._**management**/

	- _bulb.contrib.sessions.management._**commands**/

		- **clearsession.py** (TODO)  
		<br/>

- **exceptions.py**

- **middleware.py**

- **node_models.py**

- **node_models_admin.py**

- **serializers.py**
<br/>
<br/>
<br/>



##### Database (bulb.db) :
- _bulb.db._**management**/

    - _bulb.db.management._**commands**/

        - **bulb-apply.py**  
        <br/>

- **base.py**

- **exceptions.py**

- **node_models.py**

- **Q_filter.py**

- **utils.py**
<br/>
<br/>
<br/>


##### Global resources (bulb.global_resources)
- _bulb.global_resources._**static**/

    - _bulb.global_resources.static._**global_resources**/

        - (bulb's global_resources' staticfiles)
<br/>
<br/>
<br/>


##### SFTP and CDN (bulb.sftp_and_cdn)
- _bulb.contrib.sftp_and_cdn._**management**/

    - _bulb.contrib.sftp_and_cdn.management._**commands**/

        - **bundlestatic.py**

        - **clearstatic.py**

        - **handlestatic.py**

        - **pushstatic.py**
        <br/>

- _bulb.contrib.sftp_and_cdn._**webpack_files**/

    - **.babelrc**

    - **package.json**

    - **package-lock.json**

    - **webpack.config.js**
    <br/>

- **cdn_apis.py**

- **exceptions.py**

- **sftp.py**
<br/>
<br/>
<br/>


##### Template (bulb.template)
- _bulb.contrib.template._**templatetags**/

    - **bulb_static.py**

- **context_processors.py**
<br/>
<br/>
<br/>


##### Utils (bulb.utils)
- _bulb.utils._**static**/

    - _bulb.utils.static._**utils**/

        - (bulb's utils' staticfiles)
        <br/>

- _bulb.utils._**templates**/

    - _bulb.utils.templates._**utils**/

        - (bulb's utils's templates)
        <br/>

- **utils.py**

- **views.py**
<br/>
<br/>
<br/>

##### Settings (bulb.settings)
<br/>
<br/>
<br/>
