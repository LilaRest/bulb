from bulb.contrib.auth.authentication import get_user_from_request, preserve_or_login, get_user_is_logged


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define the request.user
        request.user = get_user_from_request(request)

        request.user_is_logged = get_user_is_logged(request)
        # Preserve the user connection if it is already logged
        preserve_or_login(request)

        # Call the view
        response = self.get_response(request)

        return response
