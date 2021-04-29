from django.urls import re_path

from openscenario import views

urlpatterns = [
    re_path(r'^api/openScenario$', views.convert_open_scenario),
]
