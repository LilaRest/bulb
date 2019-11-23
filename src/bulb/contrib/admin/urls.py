from bulb.contrib.admin.views import admin_home_view, admin_logout_view, admin_login_view
from django.urls import path, include
from django.conf import settings

BULB_ADDITIONAL_ADMIN_MODULES = settings.BULB_ADDITIONAL_ADMIN_MODULES

urlpatterns = [
    path("", admin_home_view, name="admin_home"),
    path("logout/", admin_logout_view, name="admin_logout"),
    path("login/", admin_login_view, name="admin_login"),
    path("handling/", include("bulb.contrib.handling.urls")),
    path("releases/", include("bulb.contrib.releases.urls")),
    path("logs/", include("bulb.contrib.logs.urls")),
    path("activity/", include("bulb.contrib.activity.urls")),
]

for module_name, module_infos in BULB_ADDITIONAL_ADMIN_MODULES.items():
    urlpatterns.append(path(f"{module_infos['path_name']}/", include(f"{module_name}.urls")))
