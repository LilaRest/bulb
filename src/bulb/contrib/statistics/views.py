from bulb.contrib.auth.decorators import login_required, staff_only
from django.shortcuts import render
from django.conf import settings

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"

@staff_only()
@login_required(login_page_url=login_page_url)
def statistics_view(request):

    return render(request, "statistics/pages/statistics_page.html")
