from bulb.contrib.admin.views import admin_home_view, admin_logout_view
from django.urls import path, include
from django.conf import settings

BULB_ADDITIONAL_ADMIN_MODULES = settings.BULB_ADDITIONAL_ADMIN_MODULES

urlpatterns = [
    path("", admin_home_view, name="admin_home"),
    path("logout/", admin_logout_view, name="admin_logout"),
    path("handling/", include("bulb.contrib.handling.urls")),
]

for module_name, module_infos in BULB_ADDITIONAL_ADMIN_MODULES.items():
    urlpatterns.append(path(f"{module_infos['path_name']}/", include(f"{module_name}.urls")))


