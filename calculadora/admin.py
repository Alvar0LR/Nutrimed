from django.contrib import admin
from .models import CalculoEnergetico


@admin.register(CalculoEnergetico)
class CalculoEnergeticoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha', 'peso', 'altura', 'imc', 'clasificacion_imc', 'tmb', 'get']
    list_filter = ['sexo', 'actividad', 'clasificacion_imc']
    search_fields = ['usuario__username']
    readonly_fields = ['imc', 'clasificacion_imc', 'tmb', 'get', 'proteinas_g', 'hidratos_g', 'grasas_g']