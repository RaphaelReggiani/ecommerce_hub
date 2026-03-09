from django.urls import path

from ..ech_web import views

urlpatterns = [
    path("home/", views.home, name="home"),
]