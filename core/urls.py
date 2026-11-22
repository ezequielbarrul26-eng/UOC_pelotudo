from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('pedir/', views.pedir, name='pedir'),
    path('plantarse/', views.plantarse, name='plantarse'),
    path('nueva/', views.nueva, name='nueva'),
    path('apostar/', views.apostar, name='apostar'),
]