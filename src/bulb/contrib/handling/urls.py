from bulb.contrib.handling.views import handling_home_view, node_model_home_view, node_model_home_search_view, node_handling_view, node_creation_view
from django.urls import path, re_path

urlpatterns = [
    path("", handling_home_view, name="handling_home"),
    re_path(r"^(?P<node_model_name>[a-zA-Z_]+)$", node_model_home_view, name="node_model_home"),
    re_path(r"^(?P<node_model_name>[a-zA-Z_]+)/recherche$", node_model_home_search_view, name="node_model_home_search"),
    re_path(r"^(?P<node_model_name>[a-zA-Z_]+)/(?P<node_uuid>([a-z0-9]{32}|None))$", node_handling_view, name="node_handling"),
    re_path(r"^(?P<node_model_name>[a-zA-Z_]+)/creation", node_creation_view, name="node_creation"),
]
