from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_alimentos, name='lista_alimentos'),
    path('nuevo/', views.crear_alimentos, name='crear_alimento'),
    path('<int:id>/editar/', views.actualizar_alimentos, name='editar_alimento'),
    path('<int:id>/eliminar/', views.eliminar_alimentos, name='eliminar_alimento'),
    path('comidas/', views.lista_comidas, name='lista_comidas'),
    path('comidas/nueva/', views.crear_comida, name='crear_comida'),
    path('comidas/<int:id>/eliminar/', views.eliminar_comida, name='eliminar_comida'),
    path('comidas/<int:id>/editar/', views.editar_comida, name='editar_comida')
]