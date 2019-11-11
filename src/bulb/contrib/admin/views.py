from bulb.contrib.auth.decorators import login_required, protect_authentication_view, staff_only
from bulb.contrib.auth.authentication import preserve_or_login, authenticate

from bulb.contrib.auth.authentication import force_clear_user_session
from bulb.contrib.admin.forms import AdminLoginForm

from bulb.contrib.auth.node_models import AnonymousUser, get_user_node_model
from bulb.db import gdbh

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"
home_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/"

User = get_user_node_model()

@staff_only(if_false_url=f"/{settings.BULB_ADMIN_BASEPATH_NAME}/login")
@login_required(login_page_url=f"/{settings.BULB_ADMIN_BASEPATH_NAME}/login")
def admin_home_view(request):
    return render(request, "admin/pages/admin_home.html")

@protect_authentication_view(home_page_url=f"/{settings.BULB_ADMIN_BASEPATH_NAME}/")
def admin_login_view(request):
    form = AdminLoginForm(request.POST or None)

    if request.POST:
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(email, password)

            if isinstance(user, User):
                preserve_or_login(request, user)
                return redirect(f"/{settings.BULB_ADMIN_BASEPATH_NAME}/")

    return render(request, 'admin/pages/login.html', {'form': form})


@staff_only()
def admin_logout_view(request):
    if "next" in request.POST:
        force_clear_user_session(request)
        return redirect(f"{login_page_url}/?next={request.POST.get('next')}")

    else:
        force_clear_user_session(request)
        return redirect(login_page_url)
