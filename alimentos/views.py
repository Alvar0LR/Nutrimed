from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .repositories import AlimentoRepository
from .forms import AlimentoForm

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
