from bulb.contrib.auth.authentication import get_user_is_logged, get_user_from_request
from bulb.contrib.auth.node_models import get_anonymoususer_node_model
from django.conf import settings
from django.shortcuts import redirect, render

AnonymousUser = get_anonymoususer_node_model()


def login_required(login_page_url=settings.BULB_LOGIN_URL):
    """
    If the user is logged, execute the decorated view, else redirect to 'login_page_url

    :param login_page_url: The page to which one redirect the user if it is not logged.
    """
    def decorator(related_function):

        def wrapped_function(request, *args, **kwargs):

            try:
                # Support wsgi.
                current_path = request.environ["PATH_INFO"]

            except AttributeError:
                # Support asgi.
                current_path = request.__dict__["META"]["PATH_INFO"]

            if get_user_is_logged(request):
                return related_function(request, *args, **kwargs)
            else:
                return redirect(login_page_url + f"/?next={current_path}")

        return wrapped_function
    return decorator


def protect_authentication_view(home_page_url=settings.BULB_HOME_PAGE_URL):
    """
    If the user is already logged, the login view (and the page that it sent), is not accessible, the decorator
    automatically redirect the user to the home page.

    :param home_page_url: The url of the home page (ex: '/blog/home/')
    """

    def decorator(related_function):

        def wrapped_function(request, *args, **kwargs):
            if get_user_is_logged(request):
                return redirect(home_page_url, permanent=True)
            else:
                return related_function(request, *args, **kwargs)

        return wrapped_function
    return decorator


def permission_required(permission_codename, if_false_html=None, if_false_url=settings.BULB_HOME_PAGE_URL):
    """
    If the user has the permission, execute the decorated view, else redirect to 'if_false_url'.

    :param permission_codename: The codename of the permission.

    :param if_false_html: The html page rendered, if the user doesn't have the permission.

    :param if_false_url: The url of the page to which one redirect the user, if the user doesn't have the
                         permission.
    """
    def decorator(related_function):

        def wrapped_function(request, *args, **kwargs):
            user = get_user_from_request(request)

            # if not AnonymousUser in user.__class__.__mro__:
            if not isinstance(user, AnonymousUser):
                if isinstance(permission_codename, str):
                    if user.has_perm(permission_codename) or user.is_super_user:
                        return related_function(request, *args, **kwargs)

            if if_false_html is not None:
                return render(request, if_false_html)

            else:
                return redirect(if_false_url)

        return wrapped_function
    return decorator


def staff_only(if_false_html=None, if_false_url=settings.BULB_HOME_PAGE_URL):
    """
    If the user has the permission, execute the decorated view, else redirect to 'if_false_url'.

    :param if_false_html: The html page rendered, if the user is not a staff user.

    :param if_false_url: The url of the page to which one redirect the user, if the user is not a staff user.
    """

    def decorator(related_function):

        def wrapped_function(request, *args, **kwargs):
            user = get_user_from_request(request)

            # if not AnonymousUser in user.__class__.__mro__:
            if not isinstance(user, AnonymousUser):
                if user.is_staff_user or user.is_super_user:
                    return related_function(request, *args, **kwargs)

            if if_false_html is not None:
                return render(request, if_false_html)

            else:
                return redirect(if_false_url)

        return wrapped_function

    return decorator


def super_user_only(if_false_html=None, if_false_url=settings.BULB_HOME_PAGE_URL):
    """
    If the user has the permission, execute the decorated view, else redirect to 'if_false_url'.

    :param if_false_html: The html page rendered, if the user is not a super user.

    :param if_false_url: The url of the page to which one redirect the user, if the user is not a super user.
    """

    def decorator(related_function):

        def wrapped_function(request, *args, **kwargs):
            user = get_user_from_request(request)

            # if not AnonymousUser in user.__class__.__mro__:
            if not isinstance(user, AnonymousUser):
                if user.is_super_user:
                    return related_function(request, *args, **kwargs)

            if if_false_html is not None:
                return render(request, if_false_html)

            else:
                return redirect(if_false_url)

        return wrapped_function

    return decorator
