"""
URL configuration for nutrimed project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from alimentos import views as alimentos_views
from django.contrib import admin

admin.site.site_header = "NutriMed Admin"
admin.site.site_title = "NutriMed"
admin.site.index_title = "Panel de administración"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('alimentos/', include('alimentos.urls')),
    path('plan/', alimentos_views.plan_semanal, name='plan_semanal'),
    path('plan/asignar/', alimentos_views.asignar_slot, name='asignar_slot'),
    path('plan/quitar/', alimentos_views.quitar_slot, name='quitar_slot'),
    path('plan/seleccionar/<str:fecha>/<str:turno>/', alimentos_views.seleccionar_comida_slot, name='seleccionar_comida_slot'),
    path('calculadora/', include('calculadora.urls')),
    path('accounts/', include('allauth.urls')),
]
