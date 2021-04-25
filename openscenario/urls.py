from django.urls import re_path

from openscenario import views

urlpatterns = [
    re_path(r'^action/open_scenario$', views.convert_open_scenario),
    re_path(r'^action/open_drive$', views.convert_open_drive),
]
