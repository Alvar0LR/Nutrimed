from .models import PerfilUsuario


def cookies_status(request):
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            cookies_decididas = perfil.cookies_aceptadas is not None
        except PerfilUsuario.DoesNotExist:
            cookies_decididas = False
    else:
        cookies_decididas = True  # No autenticado, no mostrar banner

    return {'cookies_decididas': cookies_decididas}