from bulb.contrib.releases.views import releases_view
from django.urls import path

urlpatterns = [
    path("", releases_view, name="releases"),
]
