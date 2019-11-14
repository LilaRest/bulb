from bulb.contrib.auth.authentication import get_user_from_request, get_user_is_logged


def user_context_processors(request):
    return {'user': get_user_from_request(request),
            'user_is_logged': get_user_is_logged(request),
            }
