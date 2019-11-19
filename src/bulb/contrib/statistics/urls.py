from bulb.contrib.statistics.views import statistics_view
from django.urls import path

urlpatterns = [
    path("", statistics_view, name="statistics"),
]
