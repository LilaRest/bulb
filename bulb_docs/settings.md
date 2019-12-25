### >> Settings :
Here you can find all the **settings.py** variable to interact with **bulb**.
Note that all the parameters created or updated by **bulb** are prefixed by **BULB**.

---
<br/>

```python
set_bulb_settings_on(locals())


################################################################
#                        bulb's variables                      #
################################################################



#################
# BULB DATABASE #
#################

# This parameter defines the attempts number where the application will retry to establish the initial connection with
# the Neo4j database (each attempt is separated by 1 second).
# It prevents failed when the database takes a long time to start or restart.
# Explanations here :
# https://neo4j.com/docs/operations-manual/3.0/deployment/post-installation/#post-installation-wait-for-start
BULB_INITIAL_CONNECTION_ATTEMPTS_NUMBER = 8 # During development and for a faster local server, you could set this variable on 2.

# Neo4j authentication :
BULB_DATABASE_URI = "bolt://localhost:7687"

BULB_DATABASE_ID = 'neo4j'

BULB_DATABASE_PASSWORD = 'neo4j'

# Encrypting trafic between the Neo4j driver and the Neo4j instance.
# Explanations here : https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#driver-authentication-encryption
BULB_DATABASE_ENCRYPTED = True

# Verification against "man-in-the-middle" attack.
# Explanations : https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#_trust
# Choices :
# 0 : TRUST_ON_FIRST_USE     (Deprecated)
# 1 : TRUST_SIGNED_CERTIFICATES     (Deprecated)
# 2 : TRUST_ALL_CERTIFICATES
# 3 : TRUST_CUSTOM_CA_SIGNED_CERTIFICATES
# 4 : TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
# 5 : TRUST_DEFAULT = TRUST_ALL_CERTIFICATES
BULB_DATABASE_TRUST = 2

# These parameters define the transactions modalities (after the establishment of the initial connection)
# Explanations here : https://neo4j.com/docs/api/python-driver/current/driver.html#max-connection-lifetime
BULB_DATABASE_MAX_CONNECTION_LIFETIME = 60 * 60

BULB_DATABASE_MAX_CONNECTION_POOL_SIZE = 50

BULB_DATABASE_CONNECTION_ACQUISITION = 60

BULB_DATABASE_CONNECTION_TIMEOUT = 15

BULB_DATABASE_MAX_RETRY_TIME = 15



##############
# BULB NODES #
##############

# Useful for development time, useless for production. But it is recommended to do a test with False before deployment,
# and to search eventual warnings in terminal's output.
# NB : The neo4j's 'apoc' plugin is required for this functionality.
BULB_CREATE_PROPERTY_IF_NOT_FOUND = True



#################
# BULB SESSIONS #
#################

BULB_SESSION_NODE_MODEL_FILE = "bulb.contrib.sessions.node_models"

BULB_SESSION_CHANGE_ON_EVERY_REQUEST = False

# You can define all the SESSION_ variables like with the native Django package.
SESSION_ENGINE = 'bulb.contrib.sessions.backends.db'

SESSION_SERIALIZER = 'bulb.contrib.sessions.serializers.JSONSerializer'  # modified

SESSION_COOKIE_AGE = 60 * 60 * 24



#######################
# BULB AUTHENTICATION #
#######################
BULB_WEBSITE_URL = "http://127.0.0.1:8000"

BULB_LOGIN_URL = '/login/'

BULB_HOME_PAGE_URL = '/home/'

BULB_LOGIN_REDIRECT_URL = '/home/'

BULB_LOGOUT_REDIRECT_URL = None  # TODO

BULB_USER_NODE_MODEL_FILE = "bulb.contrib.auth.node_models"

BULB_ANONYMOUSUSER_NODE_MODEL_FILE = "bulb.contrib.auth.node_models"

BULB_PERMISSION_NODE_MODEL_FILE = "bulb.contrib.auth.node_models"

BULB_GROUP_NODE_MODEL_FILE = "bulb.contrib.auth.node_models"

# Enable email confirmation for users registration.
BULB_REGISTRATION_USE_EMAIL_CONFIRMATION = False

BULB_CONFIRMATION_VIEW_PATH = f"{ BULB_WEBSITE_URL }/auth/confirmation/" # Url that redirect to the email_confirmation_view (bulb.contrib.auth.views)

BULB_USER_EMAIL_PROPERTY_NAME = "email" # The name of the user's property that contain its email address

BULB_EMAIL_CONFIRMATION_TEMPLATE_PATH = "authentication/background_pages/confirmation_email.html" # The path of the template of the confirmation mail

BULB_EMAIL_CONFIRMATION_SENDER_NAME = "my-email@address.com" # Email or sender's name, it depends of the email provider (if one doesn't work, try the other)

BULB_EMAIL_CONFIRMATION_SUBJECT = "Confirm your email address"

BULB_EMAIL_CONFIRMATION_DEFAULT_MESSAGE = "To confirm your email address, please follow this link : " # Text message for users who don't accept HTML email rendering

# Django email tools required variables :

# Host for sending email.
EMAIL_HOST = 'smtp.myemailserver.com'

# Port for sending email.
EMAIL_PORT = 587

# Whether to send SMTP 'Date' header in the local time zone or in UTC.
EMAIL_USE_LOCALTIME = True

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = 'my-email@address.com'

EMAIL_HOST_PASSWORD = "mypassword"

EMAIL_USE_TLS = True

EMAIL_USE_SSL = False

EMAIL_SSL_CERTFILE = None

EMAIL_SSL_KEYFILE = None

EMAIL_TIMEOUT = None


###############
# BULB PEPPER #
###############

# WARNING : Please generate your own pepper strings.
BULB_PEPPER_1 = '5Y"X,ò²-<]1%ô4A³£a¬Ë!tmzü.åÇ6Þ'

BULB_PEPPER_2 = 'é¿4<fiu-0A{ï"Z§íÒj|¶Äò¼õ!úVÿUq*0q¶&SHÁ,¯-7q&¿'



#############
# BULB SFTP #
#############
BULB_USE_SFTP = False

BULB_SFTP_HOST = None

BULB_SFTP_HOST_SSH_KEY = None

BULB_SFTP_PORT = None

BULB_SFTP_USER = None

BULB_SFTP_PASSWORD = None

BULB_SFTP_PRIVATE_KEY_PATH = None

BULB_SFTP_PRIVATE_KEY_PASS = None

BULB_SFTP_PULL_URL = None



#############################
# BULB SFTP SRC STATICFILES #
#############################

"""
Possible values :
    - "raw" : The 'staticfiles' folder will be pushed on the sftp.
    - "bundled" : The "bundled_staticfiles" folder will be created from the 'staticfiles' folder and will be pushed
                  on the sftp.
    - "both" : Both 'staticfiles' and 'bundled_staticfiles' folders will be pushed on the sftp.
"""
BULB_SFTP_SRC_STATICFILES_MODE = "bundled"

"""
The webpack polyfill is the easiest way to implement polyfills for the entire website.
Just set this variable on True and all your scripts will be compatible for all browsers of all versions.

But to obtain a more powerful website, it is recommended to don't use the webpack polyfill because:
- The webpack polyfill is directly implemented into your bundle scripts, this means that if one of your scripts doesn't
  need all polyfills , they will still be loaded.
- The webpack polyfill don't have any regard on the browser used to load a page. This means that if your page is open
  on a modern browser which doesn't need any polyfills, they will still be loaded.

Best solution : Use 'polyfill.io' which one will load a the polyfills required in each different context.
See : (TODO: Add the related documentation).

A good configuration of polyfill.io :
    <script crossorigin="anonymous" src="https://polyfill.io/v3/polyfill.min.js?flags=gated&features=blissfuljs%2Cdefault%2Ces2015%2Ces2016%2Ces2017%2Ces5%2Ces6%2Ces7"></script>
(Implement this script tag as the first script tag of each page which could need some polyfills.)
"""
BULB_SRC_BUNDLES_USE_WEBPACK_POLYFILL = False



############
# BULB CDN #
############

# CDN77:
BULB_USE_CDN77 = False

BULB_CDN77_LOGIN = None

BULB_CDN77_API_KEY = None

BULB_CDN77_RESOURCE_ID = None  # See : https://client.cdn77.com/support/api/version/2.0/cdn-resource#List



##############
# BULB ADMIN #
##############

BULB_ADMIN_BASEPATH_NAME = "admin" # If "admin", the administration will be accessible at mywebsite.com/admin/

# Format {"<application name>": {"printed_name": "xxx",
#                                "path_name": "xxx",
#                                "home_view_url_name": "xxx"},
#        }
BULB_ADDITIONAL_ADMIN_MODULES = {}



################################################################
#                      bulb used variables                     #
################################################################

# The first hasher in this list is the preferred algorithm.  Any password using different algorithms will be converted
# automatically upon login.
PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ]

# SASS INTEGRATION.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

COMPRESS_OFFLINE = True

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

```
<br/>
<br/>
<br/>
