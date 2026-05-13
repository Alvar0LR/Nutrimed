from django import forms
from .models import CalculoEnergetico


class CalculoEnergeticoForm(forms.ModelForm):
    class Meta:
        model = CalculoEnergetico
        fields = ['sexo', 'edad', 'peso', 'altura', 'actividad']
        widgets = {
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 100}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'min': 20, 'max': 300, 'step': '0.1'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control', 'min': 100, 'max': 250}),
            'actividad': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'sexo': 'Sexo biológico',
            'edad': 'Edad (años)',
            'peso': 'Peso actual (kg)',
            'altura': 'Altura (cm)',
            'actividad': 'Nivel de actividad física',
        }