from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculadora, name='calculadora'),
    path('eliminar/<int:pk>/', views.eliminar_calculo, name='eliminar_calculo'),
]