from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Alimentos(models.Model):
    GRUPOS = [
       ('verdura', 'Verdura'),
        ('fruta', 'Fruta'),
        ('cereal', 'Cereal'),
        ('legumbre', 'Legumbre'),
        ('proteina', 'Proteína'),
        ('lacteo', 'Lácteo'),
        ('grasa', 'Grasa'),
        ('otro', 'Otro'),
    ]
    
    PERFIL = [
         ('apto', 'Apto'),
        ('moderado', 'Moderado'),
        ('evitar', 'Evitar'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    grupo = models.CharField(max_length=50, choices=GRUPOS)
    calorias = models.DecimalField(max_digits=6, decimal_places=2)
    proteinas = models.DecimalField(max_digits=5, decimal_places=2)
    hidratos = models.DecimalField(max_digits=5, decimal_places=2)
    grasas = models.DecimalField(max_digits=5, decimal_places=2)
    fibra = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sodio = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    perfil_medico = models.CharField(max_length=20, choices=PERFIL, default='apto')
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
class Comida(models.Model):
    TURNOS = [
            ('desayuno', 'Desayuno'),
            ('almuerzo', 'Almuerzo'),
            ('comida', 'Comida'),
            ('merienda', 'Merienda'),
            ('cena', 'Cena'),
        ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    turno = models.CharField(max_length=20, choices=TURNOS)
    ingredientes = models.ManyToManyField(Alimentos, through="ComidaIngrediente")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        
    def __str__(self):
        return self.nombre

    def calcular_macros(self):
        totales = {'calorias': 0, 'proteinas': 0, 'hidratos': 0, 'grasas': 0}
        for ci in self.comidaingrediente_set.all():
            factor = ci.cantidad / 100
            totales['calorias'] += float(ci.alimento.calorias) * factor
            totales['proteinas'] += float(ci.alimento.proteinas) * factor
            totales['hidratos'] += float(ci.alimento.hidratos) * factor
            totales['grasas'] += float(ci.alimento.grasas) * factor
        return {k: round(v,1) for k, v in totales.items()}
            


class ComidaIngrediente(models.Model):
    comida = models.ForeignKey(Comida, on_delete=models.CASCADE)
    alimento = models.ForeignKey(Alimentos, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=6, decimal_places=2, help_text='Cantidad')
    
    def __str__(self):
        return f'{self.alimento.nombre} - {self.cantidad}g'
    

class SlotDieta(models.Model):
    TURNOS = [
            ('desayuno', 'Desayuno'),
            ('almuerzo', 'Almuerzo'),
            ('comida', 'Comida'),
            ('merienda', 'Merienda'),
            ('cena', 'Cena'),
        ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comida = models.ForeignKey(Comida, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateField()
    turno = models.CharField(max_length=20, choices=TURNOS)

    class Meta:
        unique_together = ['usuario', 'fecha', 'turno']
    
    def __str__(self):
        return f'{self.usuario} - {self.fecha} - {self.turno}'