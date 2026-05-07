from django import forms
from .models import Alimentos

class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimentos
        fields = ['nombre', 'grupo', 'calorias', 'proteinas', 'hidratos', 'grasas', 'fibra', 'sodio', 'azucares', 'perfil_medico', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Lentejas crudas'}),
            'grupo': forms.Select(attrs={'class': 'form-control'}),
            'calorias': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kcal por 100g'}),
            'proteinas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g por 100g'}),
            'hidratos': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g por 100g'}),
            'grasas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g por 100g'}),
            'fibra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g por 100g'}),
            'sodio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mg por 100g'}),
            'perfil_medico': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas clínicas opcionales...'}),
            'azucares': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'g por 100g'}),
        }

