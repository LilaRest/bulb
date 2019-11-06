from bulb.contrib.handling.node_models import WebsiteSettings
from django.shortcuts import render
from django.conf import settings


class HandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Call the view
        response = self.get_response(request)

        settings_object = WebsiteSettings.get()

        if settings_object:
            admin_base_path_name = settings.BULB_ADMIN_BASEPATH_NAME

            # Redirect to the maintenance page if the user is neither a super_user nor a staff_user.
            if settings_object.maintenance:
                if request.user.is_super_user:
                    pass

                elif request.user.is_staff_user:
                    if request.environ["PATH_INFO"].split("/")[1] != admin_base_path_name:
                        return render(request, "handling/pages/maintenance.html")

                else:
                    return render(request, "handling/pages/maintenance.html")

        return response
