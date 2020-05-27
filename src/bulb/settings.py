import os


class BULB_BASE_DIRError(Exception):
    pass


def set_bulb_settings_on(root_settings):
    """
    This function overwrite many settings variables from the project's settings.py file, in order
    to add the bulb modules to the project but also to make compatible the django project with bulb.
    :param root_settings: The locals() dict of the project settings.py file
    """
    # Set the BASE_DIR variable as environment variable.
    try:
        BASE_DIR = root_settings['BASE_DIR']

    except KeyError:
        bulb_logger.error(
            'BULB_BASE_DIRError("You must define the default BASE_DIR variable into the settings.py file of your project.")')
        raise BULB_BASE_DIRError("You must define the default BASE_DIR variable into the settings.py file of your project.")

    else:
        os.environ["BASE_DIR"] = BASE_DIR

    # Add the bulb module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb')

    # Remove the native auth module and set the bulb one.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.auth', ]

    else:
        if 'django.contrib.auth' in INSTALLED_APPS:
            INSTALLED_APPS.remove('django.contrib.auth')
            INSTALLED_APPS.insert(0, 'bulb.contrib.auth')
        else:
            pass
            INSTALLED_APPS.insert(0, 'bulb.contrib.auth')

    # Remove the native admin module and set the bulb one.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.admin', ]

    else:
        if 'django.contrib.admin' in INSTALLED_APPS:
            INSTALLED_APPS.remove('django.contrib.admin')
            INSTALLED_APPS.insert(0, 'bulb.contrib.admin')
        else:
            INSTALLED_APPS.insert(0, 'bulb.contrib.admin')

    # Remove the native contenttypes module and set the bulb one.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        pass
        # root_settings['INSTALLED_APPS'] = ['bulb.contrib.contenttypes', ]

    else:
        if 'django.contrib.contenttypes' in INSTALLED_APPS:
            INSTALLED_APPS.remove('django.contrib.contenttypes')
            # INSTALLED_APPS.insert(0, 'bulb.contrib.contenttypes')
        else:
            pass
            # INSTALLED_APPS.insert(0, 'bulb.contrib.contenttypes')

    # Remove the native sessions module and set the bulb one.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.sessions', ]

    else:
        if 'django.contrib.sessions' in INSTALLED_APPS:
            INSTALLED_APPS.remove('django.contrib.sessions')
            INSTALLED_APPS.insert(0, 'bulb.contrib.sessions')
        else:
            pass
            INSTALLED_APPS.insert(0, 'bulb.contrib.sessions')

    # Add the bulb database module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.db', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.db')

    # Add the bulb sftp and cdn module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.sftp_and_cdn', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.sftp_and_cdn')

    # Add the bulb contrib.statictools module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.statictools', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.contrib.statictools')

    # Add the bulb contrib.handling module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.handling', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.contrib.handling')

    # Add the bulb contrib.releases module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.releases', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.contrib.releases')

    # Add the bulb contrib.activity module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.activity', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.contrib.activity')

    # Add the bulb contrib.logs module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.contrib.logs', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.contrib.logs')

    # Add the bulb template module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.template', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.template')

    # Add the bulb core module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.core', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.core')

    # Add the bulb utils module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['bulb.utils', ]

    else:
        INSTALLED_APPS.insert(0, 'bulb.utils')

    # Add the django's humanize module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['django.contrib.humanize', ]

    else:
        INSTALLED_APPS.insert(0, 'django.contrib.humanize')

    # Add the django-compressor module.
    try:
        INSTALLED_APPS = root_settings['INSTALLED_APPS']

    except KeyError:
        root_settings['INSTALLED_APPS'] = ['compressor', ]

    else:
        INSTALLED_APPS.insert(0, 'compressor')

    # Remove the native auth middleware and set the bulb one.
    try:
        MIDDLEWARE = root_settings['MIDDLEWARE']

    except KeyError:
        root_settings['MIDDLEWARE'] = ['django.contrib.auth.middleware.AuthenticationMiddleware', ]

    else:
        if 'django.contrib.auth.middleware.AuthenticationMiddleware' in MIDDLEWARE:
            MIDDLEWARE.remove('django.contrib.auth.middleware.AuthenticationMiddleware')
            MIDDLEWARE.insert(2, 'bulb.contrib.auth.middleware.AuthenticationMiddleware')
        else:
            MIDDLEWARE.insert(2, 'bulb.contrib.auth.middleware.AuthenticationMiddleware')

    # Remove the native sessions middleware and set the bulb one.
    try:
        MIDDLEWARE = root_settings['MIDDLEWARE']

    except KeyError:
        root_settings['MIDDLEWARE'] = ['bulb.contrib.sessions.middleware.SessionMiddleware', ]

    else:
        if 'django.contrib.sessions.middleware.SessionMiddleware' in MIDDLEWARE:
            MIDDLEWARE.remove('django.contrib.sessions.middleware.SessionMiddleware')
            MIDDLEWARE.insert(1, 'bulb.contrib.sessions.middleware.SessionMiddleware')
        else:
            MIDDLEWARE.insert(1, 'bulb.contrib.sessions.middleware.SessionMiddleware')

    # Set the bulb's HandlingMiddleware.
    try:
        MIDDLEWARE = root_settings['MIDDLEWARE']

    except KeyError:
        root_settings['MIDDLEWARE'] = ['bulb.contrib.handling.middleware.HandlingMiddleware']

    else:
        MIDDLEWARE.insert(1, 'bulb.contrib.handling.middleware.HandlingMiddleware')

    # Remove the native auth context processcors.
    try:
        TEMPLATES_context_processors = root_settings['TEMPLATES'][0]['OPTIONS']['context_processors']

    except KeyError:
        root_settings['TEMPLATES'][0]['OPTIONS']['context_processors'] = ['bulb.contrib.auth.context_processors.user_context_processors',]

    else:
        if 'django.contrib.auth.context_processors.auth' in TEMPLATES_context_processors:
            TEMPLATES_context_processors.remove('django.contrib.auth.context_processors.auth')
            TEMPLATES_context_processors.insert(0, 'bulb.contrib.auth.context_processors.user_context_processors')
        else:
            pass
            TEMPLATES_context_processors.insert(0, 'bulb.contrib.auth.context_processors.user_context_processors')

    # Add the bulb template 'debug' context processors.
    try:
        TEMPLATES_context_processors = root_settings['TEMPLATES'][0]['OPTIONS']['context_processors']

    except KeyError:
        root_settings['TEMPLATES'][0]['OPTIONS']['context_processors'] = ['bulb.template.context_processors.bulb_variables',]

    else:
        TEMPLATES_context_processors.insert(0, 'bulb.template.context_processors.bulb_variables')

    # Add the bulb admin 'additionnal_admin_modules' context processors.
    try:
        TEMPLATES_context_processors = root_settings['TEMPLATES'][0]['OPTIONS']['context_processors']

    except KeyError:
        root_settings['TEMPLATES'][0]['OPTIONS']['context_processors'] = [
            'bulb.contrib.admin.context_processors.additionnal_admin_modules', ]

    else:
        TEMPLATES_context_processors.insert(0, 'bulb.contrib.admin.context_processors.additionnal_admin_modules')

    # Add the bulb admin 'website_settings' context processors.
    try:
        TEMPLATES_context_processors = root_settings['TEMPLATES'][0]['OPTIONS']['context_processors']

    except KeyError:
        root_settings['TEMPLATES'][0]['OPTIONS']['context_processors'] = [
            'bulb.contrib.handling.context_processors.website_settings', ]

    else:
        TEMPLATES_context_processors.insert(0, 'bulb.contrib.handling.context_processors.website_settings')

    # Add the bulb sftp_and_cdn 'bundled_files_version' context processors.
    try:
        TEMPLATES_context_processors = root_settings['TEMPLATES'][0]['OPTIONS']['context_processors']

    except KeyError:
        root_settings['TEMPLATES'][0]['OPTIONS']['context_processors'] = [
            'bulb.sftp_and_cdn.context_processors.bundled_files_version', ]

    else:
        TEMPLATES_context_processors.insert(0, 'bulb.sftp_and_cdn.context_processors.bundled_files_version')

    # Remove the DATABASES variable :
    try:
        DATABASES = root_settings['DATABASES']

    except KeyError:
        pass

    else:
        del root_settings["DATABASES"]


    ##################
    # AUTHENTICATION #
    ##################

    # Remove the native auth backends config.
    root_settings['AUTH_USER_MODEL'] = None
    root_settings['AUTHENTICATION_BACKENDS'] = []
    root_settings['AUTH_PASSWORD_VALIDATORS'] = []

    ################################################################
    #                        bulb's variables                      #
    ################################################################

    #################
    # BULB DATABASE #
    #################

    # This parameter defines the attempts number where the application will retry to establish the initial connection
    # with the Neo4j database (each attempt is separated by 1 second).
    # It prevents failed when the database takes a long time to start or restart.
    # Explanations here :
    # https://neo4j.com/docs/operations-manual/3.0/deployment/post-installation/#post-installation-wait-for-start

    if root_settings['DEBUG']:
        root_settings['BULB_INITIAL_CONNECTION_ATTEMPTS_NUMBER'] = 2
    else:
        root_settings['BULB_INITIAL_CONNECTION_ATTEMPTS_NUMBER'] = 8

    # Neo4j authentication :
    root_settings['BULB_DATABASE_URI'] = "bolt://localhost:7687"

    root_settings['BULB_DATABASE_ID'] = 'neo4j'

    root_settings['BULB_DATABASE_PASSWORD'] = 'neo4j'

    # Encrypting trafic between the Neo4j driver and the Neo4j instance.
    # Explanations here : https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#driver-authentication-encryption
    root_settings['BULB_DATABASE_ENCRYPTED'] = True

    # Verification against "man-in-the-middle" attack.
    # Explanations : https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#_trust
    # Choices :
    # 0 : TRUST_ON_FIRST_USE     (Deprecated)
    # 1 : TRUST_SIGNED_CERTIFICATES     (Deprecated)
    # 2 : TRUST_ALL_CERTIFICATES
    # 3 : TRUST_CUSTOM_CA_SIGNED_CERTIFICATES
    # 4 : TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
    # 5 : TRUST_DEFAULT = TRUST_ALL_CERTIFICATES
    root_settings['BULB_DATABASE_TRUST'] = 2

    # These parameters define the transactions modalities (after the establishment of the initial connection)
    # Explanations here : https://neo4j.com/docs/api/python-driver/current/driver.html#max-connection-lifetime
    root_settings['BULB_DATABASE_MAX_CONNECTION_LIFETIME'] = 60 * 60

    root_settings['BULB_DATABASE_MAX_CONNECTION_POOL_SIZE'] = 50

    root_settings['BULB_DATABASE_CONNECTION_ACQUISITION'] = 60

    if root_settings["DEBUG"]:
        root_settings['BULB_DATABASE_CONNECTION_TIMEOUT'] = 0.1
    else:
        root_settings['BULB_DATABASE_CONNECTION_TIMEOUT'] = 15

    root_settings['BULB_DATABASE_MAX_RETRY_TIME'] = 15

    ##############
    # BULB NODES #
    ##############

    # Useful for development time, useless for production. But it is recommended to do a test with False before deployment,
    # and to search eventual warnings in terminal's output.
    # NB : The neo4j's 'apoc' plugin is required for this functionality.
    root_settings['BULB_CREATE_PROPERTY_IF_NOT_FOUND']  = True

    #################
    # BULB SESSIONS #
    #################

    root_settings['BULB_SESSION_NODE_MODEL_FILE'] = "bulb.contrib.sessions.node_models"

    root_settings['BULB_SESSION_CHANGE_ON_EVERY_REQUEST'] = False

    # You can define all the SESSION_ variables like with the native Django package.
    root_settings['SESSION_ENGINE'] = 'bulb.contrib.sessions.backends.db'

    root_settings['SESSION_SERIALIZER'] = 'bulb.contrib.sessions.serializers.JSONSerializer'

    root_settings['SESSION_COOKIE_AGE'] = 60 * 60 * 24

    #######################
    # BULB AUTHENTICATION #
    #######################

    root_settings['BULB_WEBSITE_URL'] = "http://127.0.0.1:8000"

    root_settings['BULB_LOGIN_URL'] = '/login/'

    root_settings['BULB_HOME_PAGE_URL'] = '/home/'

    root_settings['BULB_LOGIN_REDIRECT_URL'] = '/home/'

    root_settings['BULB_LOGOUT_REDIRECT_URL'] = None  # TODO

    root_settings['BULB_USER_NODE_MODEL_FILE'] = "bulb.contrib.auth.node_models"

    root_settings['BULB_ANONYMOUSUSER_NODE_MODEL_FILE'] = "bulb.contrib.auth.node_models"

    root_settings['BULB_PERMISSION_NODE_MODEL_FILE'] = "bulb.contrib.auth.node_models"

    root_settings['BULB_GROUP_NODE_MODEL_FILE'] = "bulb.contrib.auth.node_models"

    # Enable email confirmation for users registration.
    root_settings['BULB_REGISTRATION_USE_EMAIL_CONFIRMATION'] = False

    root_settings['BULB_CONFIRMATION_VIEW_PATH'] = f"{root_settings['BULB_WEBSITE_URL']}/auth/confirmation/"  # Url that redirect to the email_confirmation_view (bulb.contrib.auth.views)

    root_settings['BULB_USER_EMAIL_PROPERTY_NAME'] = "email"  # The name of the user's property that contain its email address

    root_settings['BULB_EMAIL_CONFIRMATION_TEMPLATE_PATH'] = "authentication/background_pages/confirmation_email.html"  # The path of the template of the confirmation mail

    root_settings['BULB_EMAIL_CONFIRMATION_SENDER_NAME'] = "my-email@address.com"  # Email or sender's name, it depends of the email provider (if one doesn't work, try the other)

    root_settings['BULB_EMAIL_CONFIRMATION_SUBJECT'] = "Confirm your email address"

    root_settings['BULB_EMAIL_CONFIRMATION_DEFAULT_MESSAGE'] = "To confirm your email address, please follow this link : "  # Text message for users who don't accept HTML email rendering

    ###############
    # BULB PEPPER #
    ###############

    # WARNING : Please generate your own pepper strings.
    root_settings['BULB_PEPPER_1'] = None

    root_settings['BULB_PEPPER_2'] = None

    #############
    # BULB SFTP #
    #############
    root_settings['BULB_USE_SFTP'] = False

    root_settings['BULB_SFTP_HOST'] = None

    root_settings['BULB_SFTP_KNOWN_HOSTS'] = None

    root_settings['BULB_SFTP_PORT'] = None

    root_settings['BULB_SFTP_USER'] = None

    root_settings['BULB_SFTP_PASSWORD'] = None

    root_settings['BULB_SFTP_PRIVATE_KEY_PATH'] = None

    root_settings['BULB_SFTP_PRIVATE_KEY_PASSWORD'] = None

    root_settings['BULB_SFTP_PULL_URL'] = None

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
    root_settings['BULB_SFTP_SRC_STATICFILES_MODE'] = "bundled"

    """
        Add a version to all bundled files. Useful to force client's caches to reload after updates.
    """
    root_settings['BULB_BUNDLED_FILES_VERSION'] = None

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
    root_settings['BULB_SRC_BUNDLES_USE_WEBPACK_POLYFILL'] = False

    ############
    # BULB CDN #
    ############

    # CDN77:
    root_settings['BULB_USE_CDN77'] = False

    root_settings['BULB_CDN77_LOGIN'] = None

    root_settings['BULB_CDN77_API_KEY'] = None

    root_settings['BULB_CDN77_RESOURCE_ID'] = None  # See : https://client.cdn77.com/support/api/version/2.0/cdn-resource#List

    ##############
    # BULB ADMIN #
    ##############

    root_settings['BULB_ADMIN_BASEPATH_NAME'] = "admin" # If "admin", the administration will be accessible at mywebsite.com/admin/

    # Format {"<application name>": {"printed_name": "xxx",
    #                                "path_name": "xxx",
    #                                "home_view_url_name": "xxx"},
    #        }
    root_settings['BULB_ADDITIONAL_ADMIN_MODULES'] = {}


    ################################################################
    #                      bulb used variables                     #
    ################################################################

    # The first hasher in this list is the preferred algorithm.  Any password using different algorithms will be
    # converted automatically upon login.
    root_settings['PASSWORD_HASHERS'] = [
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ]

    root_settings['BULB_REQUIRES_INITIAL_PATHS'] = False

    root_settings['STATIC_ROOT'] = os.path.join(root_settings["BASE_DIR"], 'staticfiles')

    if root_settings['BULB_SFTP_HOST'] is not None:
        root_settings['STATIC_URL'] = "https://" + root_settings['BULB_SFTP_HOST'] + "/"
