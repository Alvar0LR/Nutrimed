from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_alimentos, name='lista_alimentos'),
    path('nuevo/', views.crear_alimentos, name='crear_alimento'),
    path('<int:id>/editar/', views.actualizar_alimentos, name='editar_alimento'),
    path('<int:id>/eliminar/', views.eliminar_alimentos, name='eliminar_alimento'),
]