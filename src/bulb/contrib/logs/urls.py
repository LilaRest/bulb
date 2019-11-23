from bulb.contrib.logs.views import logs_view
from django.urls import path

urlpatterns = [
    path("", logs_view, name="logs"),
]
