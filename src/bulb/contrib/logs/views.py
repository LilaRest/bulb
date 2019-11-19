from bulb.contrib.auth.decorators import login_required, staff_only
from django.shortcuts import render
from django.conf import settings

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"

@staff_only()
@login_required(login_page_url=login_page_url)
def logs_view(request):

    return render(request, "logs/pages/logs_page.html")
