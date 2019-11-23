from bulb.contrib.activity.views import activity_view
from django.urls import path

urlpatterns = [
    path("", activity_view, name="activity"),
]
