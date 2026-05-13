from abc import ABC, abstractmethod
from .models import CalculoEnergetico


class BaseRepository(ABC):

    def __init__(self, usuario):
        self.usuario = usuario

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, id):
        pass

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, id):
        pass


class CalculoEnergeticoRepository(BaseRepository):

    def get_all(self):
        return CalculoEnergetico.objects.filter(usuario=self.usuario)

    def get_by_id(self, id):
        return CalculoEnergetico.objects.get(id=id, usuario=self.usuario)

    def create(self, data):
        return CalculoEnergetico.objects.create(usuario=self.usuario, **data)

    def delete(self, id):
        calculo = self.get_by_id(id)
        calculo.delete()

    def get_historial(self, limite=10):
        return CalculoEnergetico.objects.filter(
            usuario=self.usuario
        ).order_by('-fecha')[:limite]

    def get_ultimo(self):
        return CalculoEnergetico.objects.filter(
            usuario=self.usuario
        ).order_by('-fecha').first()

    def contar(self):
        return CalculoEnergetico.objects.filter(usuario=self.usuario).count()