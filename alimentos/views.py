from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .repositories import AlimentoRepository
from .forms import AlimentoForm
from .models import Comida
from .repositories import AlimentoRepository, ComidaRepository

# Create your views here.
@login_required
def lista_alimentos(request):
    repo = AlimentoRepository(request.user)
    query = request.GET.get('q', '')
    grupo = request.GET.get('grupo', '')

    if query:
        alimentos = repo.buscar(query)
    elif grupo:
        alimentos = repo.get_by_grupo(grupo)
    else:
        alimentos = repo.get_all()

    context = {
        'alimentos': alimentos,
        'query': query,
        'grupo_sel': grupo,
        'grupos': [('verdura','Verdura'),('fruta','Fruta'),('cereal','Cereal'),
                   ('legumbre','Legumbre'),('proteina','Proteína'),('lacteo','Lácteo'),
                   ('grasa','Grasa'),('otro','Otro')],
    }

    return render(request, 'alimentos/lista.html', context)


@login_required
def crear_alimentos(request):
    repo = AlimentoRepository(request.user)
    if request.method == "POST":
        form = AlimentoForm(request.POST)
        if form.is_valid():
            repo.create(form.cleaned_data)
            messages.success(request, "Ingrediente creado correctamente")
            return redirect('lista_alimentos')
    else:
        form = AlimentoForm()
    return render(request, 'alimentos/form.html', {'form': form, 'titulo': 'Nuevo ingrediente'})

@login_required
def actualizar_alimentos(request, id):
    repo = AlimentoRepository(request.user)
    alimento = repo.get_by_id(id)
    if request.method == "POST":
       form = AlimentoForm(request.POST, instance=alimento)
       if form.is_valid():
           repo.update(id, form.cleaned_data)
           messages.success(request, "Ingrediente actualizado correctamente")
           return redirect('lista_alimentos')
    else:
        form = AlimentoForm(instance=alimento)
    return render(request, 'alimentos/form.html', {'form': form, 'titulo': 'Actualizar ingrediente', 'alimento': alimento})

@login_required
def eliminar_alimentos(request, id):
    repo = AlimentoRepository(request.user)
    alimento = repo.get_by_id(id)
    if request.method == "POST":
        repo.delete(id)
        messages.success(request, "Ingrediente eliminado correctamente")
        return redirect("lista_alimentos")
    alimento = repo.get_by_id(id)
    return render(request, 'alimentos/confirmar_eliminar.html', {'alimento': alimento})


########## COMIDAS ###############


@login_required
def lista_comidas(request):
    repo = ComidaRepository(request.user)
    comidas = repo.get_all()
    comidas_con_macros = []
    for comida in comidas:
        macros = repo.calcular_macros(comida.id)
        comidas_con_macros.append({'comida': comida, 'macros': macros})
    return render(request, 'alimentos/comidas_lista.html', {'comidas': comidas_con_macros})

@login_required
def crear_comida(request):
    repo = ComidaRepository(request.user)
    alimentos = AlimentoRepository(request.user).get_all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        turno = request.POST.get('turno')
        comida = repo.create(nombre, turno)
        ingrediente_ids = request.POST.getlist('ingrediente_id')
        cantidades = request.POST.getlist('cantidad')
        for ing_id, cantidad in zip(ingrediente_ids, cantidades):
            if ing_id and cantidad:
                repo.add_ingrediente(comida, ing_id, cantidad)
        messages.success(request, 'Comida creada correctamente.')
        return redirect('lista_comidas')
    context = {
        'alimentos': alimentos,
        'turnos': Comida.TURNOS,
    }
    return render(request, 'alimentos/comidas_form.html', context)

@login_required
def editar_comida(request, id):
    repo = ComidaRepository(request.user)
    comida, ingredientes = repo.get_with_ingredientes(id)
    alimentos = AlimentoRepository(request.user).get_all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        turno = request.POST.get('turno')
        repo.update(id, nombre, turno)
        ingrediente_ids = request.POST.getlist('ingrediente_id')
        cantidades = request.POST.getlist('cantidad')
        repo.update_ingredientes(comida, ingrediente_ids, cantidades)
        messages.success(request, 'Comida actualizada correctamente.')
        return redirect('lista_comidas')
    context = {
        'comida': comida,
        'ingredientes': ingredientes,
        'alimentos': alimentos,
        'turnos': Comida.TURNOS,
    }
    return render(request, 'alimentos/comidas_editar.html', context)

@login_required
def eliminar_comida(request, id):
    repo = ComidaRepository(request.user)
    comida = repo.get_by_id(id)
    if request.method == 'POST':
        repo.delete(id)
        messages.success(request, 'Comida eliminada.')
        return redirect('lista_comidas')
    return render(request, 'alimentos/comidas_confirmar_eliminar.html', {'comida': comida})