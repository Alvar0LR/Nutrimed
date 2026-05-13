from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CalculoEnergeticoForm
from .models import CalculoEnergetico


FACTOR_ACTIVIDAD = {
    'sedentario': 1.0,
    'baja': 1.1,
    'activo': 1.27,
    'muy_activo': 1.54,
}


def calcular_imc(peso, altura_cm):
    altura_m = altura_cm / 100
    imc = peso / (altura_m ** 2)
    if imc < 18.5:
        clasificacion = 'Bajo peso'
    elif imc < 25:
        clasificacion = 'Normopeso'
    elif imc < 30:
        clasificacion = 'Sobrepeso'
    elif imc < 35:
        clasificacion = 'Obesidad grado I'
    elif imc < 40:
        clasificacion = 'Obesidad grado II'
    else:
        clasificacion = 'Obesidad grado III'
    return round(imc, 2), clasificacion


def calcular_tmb_mifflin(sexo, peso, altura_cm, edad):
    if sexo == 'H':
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad + 5
    else:
        tmb = 10 * peso + 6.25 * altura_cm - 5 * edad - 161
    return round(tmb, 2)


def calcular_macros(get_kcal):
    proteinas_kcal = get_kcal * 0.15
    hidratos_kcal = get_kcal * 0.55
    grasas_kcal = get_kcal * 0.30
    proteinas_g = round(proteinas_kcal / 4, 2)
    hidratos_g = round(hidratos_kcal / 4, 2)
    grasas_g = round(grasas_kcal / 9, 2)
    return proteinas_g, hidratos_g, grasas_g


@login_required
def calculadora(request):
    resultado = None
    historial = CalculoEnergetico.objects.filter(usuario=request.user)[:10]

    # Si viene un id por GET, cargar ese registro para observarlo
    ver_id = request.GET.get('ver')
    if ver_id:
        calculo_ver = get_object_or_404(CalculoEnergetico, id=ver_id, usuario=request.user)
        form = CalculoEnergeticoForm(instance=calculo_ver)
        resultado = calculo_ver
    else:
        form = CalculoEnergeticoForm()

    if request.method == 'POST':
        form = CalculoEnergeticoForm(request.POST)
        if form.is_valid():
            calculo = form.save(commit=False)
            calculo.usuario = request.user

            peso = float(calculo.peso)
            altura = int(calculo.altura)
            edad = int(calculo.edad)
            sexo = calculo.sexo
            actividad = calculo.actividad

            imc, clasificacion = calcular_imc(peso, altura)
            tmb = calcular_tmb_mifflin(sexo, peso, altura, edad)
            get = round(tmb * FACTOR_ACTIVIDAD[actividad], 2)
            proteinas_g, hidratos_g, grasas_g = calcular_macros(get)

            calculo.imc = imc
            calculo.clasificacion_imc = clasificacion
            calculo.tmb = tmb
            calculo.get = get
            calculo.proteinas_g = proteinas_g
            calculo.hidratos_g = hidratos_g
            calculo.grasas_g = grasas_g
            calculo.save()

            resultado = calculo
            historial = CalculoEnergetico.objects.filter(usuario=request.user)[:10]

    return render(request, 'calculadora/calculadora.html', {
        'form': form,
        'resultado': resultado,
        'historial': historial,
    })


@login_required
def eliminar_calculo(request, pk):
    calculo = get_object_or_404(CalculoEnergetico, pk=pk, usuario=request.user)
    if request.method == 'POST':
        calculo.delete()
    return redirect('calculadora')