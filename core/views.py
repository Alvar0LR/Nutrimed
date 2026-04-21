from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'account/login.html')

@login_required
def dashboard(request):
    context = {'user_email': request.user.email}
    return render(request, 'core/dashboard.html', context)

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('landing')