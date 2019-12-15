from django.urls import path

from inspector import views

urlpatterns = [
    path('', views.index),
]