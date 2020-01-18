from bulb.contrib.auth.exceptions import BULBLoginError
from bulb.contrib.auth.node_models import get_user_node_model, get_anonymoususer_node_model
from bulb.contrib.auth.hashers import _check_password
from bulb.utils.log import bulb_logger
from bulb.db.base import gdbh
from django.conf import settings
import os

BASE_DIR = os.environ["BASE_DIR"]

User = get_user_node_model()
AnonymousUser = get_anonymoususer_node_model()


def authenticate(email, password):
    user = User.get(email=email)

    if not isinstance(user, AnonymousUser):
        if _check_password(password, user.password):
            if user.is_active_user:
                return user

    return AnonymousUser()


def _login_user(request, user):
    request.session['logged_user_uuid'] = user.uuid
    request.session.save()

    request.user = user

    gdbh.w_transaction("""
        MATCH (u:User {uuid: '%s'}), (s:Session {session_key: '%s'})
        CREATE (s)-[:IS_SESSION_OF]->(u)
    """ % (user.uuid, request.session.session_key))


def preserve_or_login(request, if_authentication_user=AnonymousUser()):
    from_authentication_user = AnonymousUser()
    from_request_user = AnonymousUser()

    try:
        if not isinstance(if_authentication_user, AnonymousUser):
            if isinstance(if_authentication_user, User):
                from_authentication_user = if_authentication_user

        if not isinstance(request.user, AnonymousUser):
            if isinstance(request.user, User):
                from_request_user = request.user

        if isinstance(if_authentication_user, AnonymousUser) and isinstance(request.user, AnonymousUser): #changed
            bulb_logger.error(
                'BULBLoginError("To login an user with the \'preserve_or_login()\' function, you must provide as function\'s parameters : the request and the user object.")')
            raise BULBLoginError(
                "To login an user with the 'preserve_or_login()' function, you must provide as function's parameters : the request and the user object.")

    except BULBLoginError:
        force_clear_user_session(request)
        bulb_logger.error(
            'BULBLoginError("To login an user with the \'preserve_or_login()\' function, you must provide as function\'s parameters : the request and the user object.")')
        raise

    else:

        # If the function is called during an authentication, to login an user :
        if not isinstance(from_authentication_user, AnonymousUser):

            # Prevent double authentication :
            if "logged_user_uuid" in request.session:
                if request.session["logged_user_uuid"] is not None:

                    #If the user is the same in database and session :
                    if from_request_user.uuid == from_authentication_user.uuid == request.session['logged_user_uuid']:
                        current_user_session = from_authentication_user.session.get()[0]

                        # If the session is the same in database and in cookie :
                        if current_user_session and request.session.session_key \
                                and current_user_session.session_key == request.session.session_key:

                            # If settings.BULB_SESSION_CHANGE_ON_EVERY_REQUEST is True, delete and create a new session
                            # Else, just preserve the current session.
                            if settings.BULB_SESSION_CHANGE_ON_EVERY_REQUEST:
                                force_clear_user_session(request, user=from_authentication_user)
                                _login_user(request, from_authentication_user)


                    else:
                        force_clear_user_session(request, user=from_authentication_user)
                        _login_user(request, from_authentication_user)

                else:
                    force_clear_user_session(request, user=from_authentication_user)
                    _login_user(request, from_authentication_user)

            else:
                force_clear_user_session(request, user=from_authentication_user)
                _login_user(request, from_authentication_user)

        # If the user is not provided during authentication (he is the currently logged user stored in request.user)
        elif not isinstance(from_request_user, AnonymousUser):

            # If a 'logged_user_uuid' is already in the session (if the user is MAYBE already logged) :
            if "logged_user_uuid" in request.session:
                if request.session['logged_user_uuid'] is not None:

                    # If the user is the same in database and session :
                    if from_request_user.uuid == request.session['logged_user_uuid']:
                        session_request = from_request_user.session.get()
                        current_user_session = None

                        if session_request is not None:
                            current_user_session = session_request[0]

                        # If the session is the same in database and in cookie :
                        if current_user_session and request.session.session_key \
                                and current_user_session.session_key == request.session.session_key:

                            # If settings.BULB_SESSION_CHANGE_ON_EVERY_REQUEST is True, delete and create a new session
                            # Else, just preserve the current session.
                            if settings.BULB_SESSION_CHANGE_ON_EVERY_REQUEST:
                                force_clear_user_session(request)
                                _login_user(request, from_request_user)

                        # If the sessions datas are not identical
                        else:
                            force_clear_user_session(request)

                    # If the users datas are not identical
                    else:
                        force_clear_user_session(request)

                # Else if the user is not already logged in :
                else:
                    force_clear_user_session(request)

            else:
                force_clear_user_session(request)


# Logout function : clear the sessions stored in the cookie and in the database + set request.user with an instance
# of AnonymousUsers
def force_clear_user_session(request, user=None):

    if not isinstance(request.user, AnonymousUser):
        gdbh.w_transaction("""
            MATCH (:User {uuid: '%s'})<-[:IS_SESSION_OF]-(s:Session)
            DETACH DELETE (s)
        """ % (request.user.uuid))

    if user is not None:
        if not isinstance(user, AnonymousUser):
            gdbh.w_transaction("""
                MATCH (:User {uuid: '%s'})<-[:IS_SESSION_OF]-(s:Session)
                DETACH DELETE (s)
            """ % (user.uuid))

    request.session.flush()
    request.user = AnonymousUser()
    request.session.setdefault('logged_user_uuid', None)


# Return the user from the request, if there is'nt, return an instance of AnonymousUser
def get_user_from_request(request):
    try:
        if 'logged_user_uuid' in request.session:

            if request.session['logged_user_uuid'] is not None:
                logged_user_uuid = request.session['logged_user_uuid']

                if logged_user_uuid is not None:

                    logged_user = User.get(uuid=logged_user_uuid)

                    if not isinstance(logged_user, AnonymousUser):
                        return logged_user

                    else:
                        # If the user does not exist, clear the session datas, that has nothing to do here
                        request.session.flush()
                        return AnonymousUser()

                else:
                    request.session.flush()
                    return AnonymousUser()

            else:
                request.session.flush()
                return AnonymousUser()

        else:
            request.session.flush()
            return AnonymousUser()

    except (AttributeError, TypeError):
        request.session.flush()
        return AnonymousUser()


# Return True if an user is logged, else return False
def get_user_is_logged(request=None, scope=None):
    # Support wsgi.
    if request is not None:
        if not AnonymousUser in request.user.__class__.__mro__:
            session_request = request.user.session.get()

            if session_request is not None:
                current_user_session = session_request[0]

                if current_user_session is not None:

                    if request.session:

                        if "logged_user_uuid" in request.session:

                            logged_user_uuid = request.session['logged_user_uuid']
                            if logged_user_uuid is not None:

                                if request.user.uuid == logged_user_uuid and \
                                        request.session.session_key == current_user_session.session_key:

                                    return True

    # Support asgi.
    elif scope is not None:
        if not AnonymousUser in scope["user"].__class__.__mro__:
            session_request = scope["user"].session.get()

            if session_request is not None:
                current_user_session = session_request[0]

                if current_user_session is not None:

                    if scope["session"]:

                        if "logged_user_uuid" in scope["session"]:

                            logged_user_uuid = scope["session"]['logged_user_uuid']
                            if logged_user_uuid is not None:

                                if scope["user"].uuid == logged_user_uuid and \
                                        scope["session"].session_key == current_user_session.session_key:

                                    return True

    else:
        return False
