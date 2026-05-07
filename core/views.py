from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from alimentos.models import SlotDieta

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'account/login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('landing')

@login_required
def dashboard(request):
    hoy = date.today()
    
   
    slots_hoy = SlotDieta.objects.filter(
        usuario=request.user,
        fecha=hoy
    ).select_related('comida')
    
    
    calorias_hoy = 0
    proteinas_hoy = 0
    hidratos_hoy = 0
    grasas_hoy = 0
    azucares_hoy = 0
    
    for slot in slots_hoy:
        if slot.comida:
            macros = slot.comida.calcular_macros()
            calorias_hoy += macros['calorias']
            proteinas_hoy += macros['proteinas']
            hidratos_hoy += macros['hidratos']
            grasas_hoy += macros['grasas']
            azucares_hoy += macros['azucares']
    
    labels = []
    datos_calorias = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        slots_dia = SlotDieta.objects.filter(usuario=request.user,fecha=dia).select_related('comida')
        
        calorias_dia = 0
        for slot in slots_dia:
            if slot.comida:
                macros = slot.comida.calcular_macros()
                calorias_dia += macros['calorias']
        
        labels.append(dia.strftime('%d %b'))
        datos_calorias.append(round(calorias_dia, 1))
    
    context = {
        'user_email': request.user.email,
        'calorias_hoy': round(calorias_hoy, 1),
        'proteinas_hoy': round(proteinas_hoy, 1),
        'hidratos_hoy': round(hidratos_hoy, 1),
        'grasas_hoy': round(grasas_hoy, 1),
        'azucares_hoy': round(azucares_hoy, 1),
        'labels': labels,
        'datos_calorias': datos_calorias,
        'slots_hoy': slots_hoy,
    }
    return render(request, 'core/dashboard.html', context)

