from django.contrib import admin
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cookies_aceptadas', 'fecha_decision_cookies']
    list_filter = ['cookies_aceptadas']