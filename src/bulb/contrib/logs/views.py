from bulb.contrib.auth.decorators import login_required, staff_only
from django.shortcuts import render
from django.conf import settings
import os

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"

@staff_only()
@login_required(login_page_url=login_page_url)
def logs_view(request):
    all_log = ""
    errors_log = ""

    with open(os.path.join(settings.BASE_DIR, "bulb.all.log"), "r") as log:
        all_log = log.read()

    with open(os.path.join(settings.BASE_DIR, "bulb.errors.log"), "r") as log:
        errors_log = log.read()

    return render(request, "logs/pages/logs_page.html", {"all_log": all_log,
                                                         "errors_log": errors_log})
