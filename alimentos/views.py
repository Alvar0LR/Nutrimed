from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .repositories import AlimentoRepository, ComidaRepository, SlotDietaRepository
from .forms import AlimentoForm
from .models import Comida, SlotDieta


@login_required
def lista_alimentos(request):
    repo = AlimentoRepository(request.user)
    query = request.GET.get('q', '').strip()
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
        'total': repo.contar(),
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
    query = request.GET.get('q','').strip()
    if query:
        comidas = repo.get_by_name(query)
    else:
        comidas = repo.get_all()

    comidas_con_macros = []
    for comida in comidas:
        macros = repo.calcular_macros(comida.id)
        comidas_con_macros.append({'comida': comida, 'macros': macros})
    return render(request, 'alimentos/comidas_lista.html', {
        'comidas': comidas_con_macros,
        'total': repo.contar(),
        'query': query
    })

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


########### SLOTDIETA ############

@login_required
def plan_semanal(request):
    repo = SlotDietaRepository(request.user)
    comidas_repo = ComidaRepository(request.user)
    
    # Calcular semana actual o la que pida el usuario
    hoy = date.today()
    semana_offset = int(request.GET.get('semana', 0))
    lunes = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=semana_offset)
    
    dias = [lunes + timedelta(days=i) for i in range(7)]
    turnos = SlotDieta.TURNOS
    slots = repo.get_semana(lunes)
    
    # Construir matriz turno x dia
    matriz = {}
    for turno_val, turno_label in turnos:
        matriz[turno_val] = {}
        for dia in dias:
            matriz[turno_val][dia] = None
    
    for slot in slots:
        if slot.turno in matriz and slot.fecha in matriz[slot.turno]:
            matriz[slot.turno][slot.fecha] = slot
    
    comidas = comidas_repo.get_all()
    
    context = {
        'dias': dias,
        'turnos': turnos,
        'matriz': matriz,
        'hoy': hoy,
        'semana_offset': semana_offset,
        'lunes': lunes,
        'comidas': comidas,
    }
    return render(request, 'plan/plan_semanal.html', context)

@login_required
def asignar_slot(request):
    if request.method == 'POST':
        repo = SlotDietaRepository(request.user)
        fecha = date.fromisoformat(request.POST.get('fecha'))
        turno = request.POST.get('turno')
        comida_id = request.POST.get('comida_id')
        repo.asignar(fecha, turno, comida_id)
    return redirect(f"/plan/?semana={request.POST.get('semana_offset', 0)}")

@login_required
def quitar_slot(request):
    if request.method == 'POST':
        repo = SlotDietaRepository(request.user)
        fecha = date.fromisoformat(request.POST.get('fecha'))
        turno = request.POST.get('turno')
        repo.quitar(fecha, turno)
    return redirect(f"/plan/?semana={request.POST.get('semana_offset', 0)}")

@login_required
def seleccionar_comida_slot(request, fecha, turno):
    repo = ComidaRepository(request.user)
    query = request.GET.get('q', '').strip()
    
    if query:
        comidas = repo.get_by_name(query)
    else:
        comidas = repo.get_all()
    
    if request.method == 'POST':
        comida_id = request.POST.get('comida_id')
        semana_offset = request.POST.get('semana_offset', 0)
        SlotDietaRepository(request.user).asignar(
            date.fromisoformat(fecha), turno, comida_id
        )
        return redirect(f"/plan/?semana={semana_offset}")
    
    context = {
        'comidas': comidas,
        'fecha': fecha,
        'turno': turno,
        'query': query,
        'turno_label': dict(SlotDieta.TURNOS).get(turno, turno),
    }
    return render(request, 'plan/seleccionar_comida.html', context)