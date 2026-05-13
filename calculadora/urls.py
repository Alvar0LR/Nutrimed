from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculadora, name='calculadora'),
    path('eliminar/<int:pk>/', views.eliminar_calculo, name='eliminar_calculo'),
    path('excel/<int:pk>/', views.exportar_excel, name='exportar_excel'),
    path('pdf/<int:pk>/', views.exportar_pdf, name='exportar_pdf'),
]