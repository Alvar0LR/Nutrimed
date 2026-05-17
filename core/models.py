from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cookies_aceptadas = models.BooleanField(null=True, default=None)
    fecha_decision_cookies = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f"Perfil de {self.usuario.email}"