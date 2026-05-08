from django.contrib import admin
from .models import Alimentos, Comida, ComidaIngrediente, SlotDieta


@admin.register(Alimentos)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'grupo', 'calorias', 'proteinas', 'hidratos', 'grasas', 'azucares', 'perfil_medico', 'usuario']
    list_filter = ['grupo', 'perfil_medico']
    search_fields = ['nombre']
    ordering = ['nombre']
    list_per_page = 20


@admin.register(Comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'turno', 'usuario', 'creado']
    list_filter = ['turno']
    search_fields = ['nombre']
    ordering = ['nombre']
    list_per_page = 20


class ComidaIngredienteInline(admin.TabularInline):
    model = ComidaIngrediente
    extra = 1
    fields = ['alimento', 'cantidad']


@admin.register(ComidaIngrediente)
class ComidaIngredienteAdmin(admin.ModelAdmin):
    list_display = ['comida', 'alimento', 'cantidad']
    search_fields = ['comida__nombre', 'alimento__nombre']
    list_per_page = 20


@admin.register(SlotDieta)
class SlotDietaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha', 'turno', 'comida']
    list_filter = ['turno']
    search_fields = ['usuario__email', 'comida__nombre']
    ordering = ['-fecha']
    list_per_page = 20