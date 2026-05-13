from django.db import models
from django.contrib.auth.models import User


class CalculoEnergetico(models.Model):
    SEXO_CHOICES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
    ]
    ACTIVIDAD_CHOICES = [
        ('sedentario', 'Sedentario (trabajo de oficina, sin ejercicio)'),
        ('baja', 'Baja actividad (ejercicio ligero 1-3 días/semana)'),
        ('activo', 'Activo (ejercicio moderado 3-5 días/semana)'),
        ('muy_activo', 'Muy activo (ejercicio intenso 6-7 días/semana)'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calculos')
    fecha = models.DateTimeField(auto_now_add=True)

    # Datos de entrada
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    edad = models.PositiveIntegerField()
    peso = models.DecimalField(max_digits=10, decimal_places=2)
    altura = models.PositiveIntegerField(help_text="Altura en cm")
    actividad = models.CharField(max_length=20, choices=ACTIVIDAD_CHOICES)

    # Resultados calculados
    imc = models.DecimalField(max_digits=10, decimal_places=2)
    clasificacion_imc = models.CharField(max_length=50)
    tmb = models.DecimalField(max_digits=10, decimal_places=2)
    get = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Gasto Energético Total")
    proteinas_g = models.DecimalField(max_digits=10, decimal_places=2)
    hidratos_g = models.DecimalField(max_digits=10, decimal_places=2)
    grasas_g = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Cálculo Energético'
        verbose_name_plural = 'Cálculos Energéticos'

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha.strftime('%d/%m/%Y')} - {self.get} kcal"