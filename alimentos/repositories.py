from abc import ABC, abstractmethod
from .models import Alimentos, Comida, ComidaIngrediente, SlotDieta
from datetime import timedelta


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


class AlimentoRepository(BaseRepository):

    def get_all(self):
        return Alimentos.objects.filter(usuario=self.usuario)

    def get_by_id(self, id):
        return Alimentos.objects.get(id=id, usuario=self.usuario)

    def create(self, data):
        return Alimentos.objects.create(usuario=self.usuario, **data)

    def delete(self, id):
        alimento = self.get_by_id(id)
        alimento.delete()

    def get_by_grupo(self, grupo):
        return Alimentos.objects.filter(usuario=self.usuario, grupo=grupo)

    def buscar(self, query):
        return Alimentos.objects.filter(usuario=self.usuario, nombre__icontains=query)

    def update(self, id, data):
        alimento = self.get_by_id(id)
        for key, value in data.items():
            setattr(alimento, key, value)
        alimento.save()
        return alimento

    def contar(self):
        return Alimentos.objects.filter(usuario=self.usuario).count()


class ComidaRepository(BaseRepository):

    def get_all(self):
        return Comida.objects.filter(usuario=self.usuario)

    def get_by_id(self, id):
        return Comida.objects.get(id=id, usuario=self.usuario)

    def create(self, *args, **kwargs):
        nombre = kwargs.get('nombre') or (args[0] if args else None)
        turno = kwargs.get('turno') or (args[1] if len(args) > 1 else None)
        return Comida.objects.create(usuario=self.usuario, nombre=nombre, turno=turno)

    def delete(self, id):
        comida = self.get_by_id(id)
        comida.delete()

    def get_by_name(self, query):
        return Comida.objects.filter(usuario=self.usuario, nombre__icontains=query)

    def add_ingrediente(self, comida, alimento_id, cantidad):
        return ComidaIngrediente.objects.create(
            comida=comida,
            alimento_id=alimento_id,
            cantidad=cantidad
        )

    def update(self, id, nombre, turno):
        comida = self.get_by_id(id)
        comida.nombre = nombre
        comida.turno = turno
        comida.save()
        return comida

    def update_ingredientes(self, comida, ingrediente_ids, cantidades):
    
        hay_validos = any(
            ing_id and cantidad and float(cantidad) > 0
            for ing_id, cantidad in zip(ingrediente_ids, cantidades)
            if cantidad
        )
    
        if not hay_validos:
            return 
    
        comida.comidaingrediente_set.all().delete()
        for ing_id, cantidad in zip(ingrediente_ids, cantidades):
            try:
                cant_float = float(cantidad)
            except (ValueError, TypeError):
                cant_float = 0
            if ing_id and cant_float > 0:
                self.add_ingrediente(comida, ing_id, cant_float)

    def get_with_ingredientes(self, id):
        comida = self.get_by_id(id)
        ingredientes = list(comida.comidaingrediente_set.select_related('alimento').all())
        return comida, ingredientes

    def calcular_macros(self, id):
        comida = self.get_by_id(id)
        return comida.calcular_macros()

    def contar(self):
        return Comida.objects.filter(usuario=self.usuario).count()


class SlotDietaRepository(BaseRepository):

    def get_all(self):
        return SlotDieta.objects.filter(usuario=self.usuario)

    def get_by_id(self, id):
        return SlotDieta.objects.get(id=id, usuario=self.usuario)

    def create(self, *args, **kwargs):
        fecha = kwargs.get('fecha')
        turno = kwargs.get('turno')
        comida_id = kwargs.get('comida_id')
        return self.asignar(fecha, turno, comida_id)

    def delete(self, id):
        slot = self.get_by_id(id)
        slot.delete()

    def get_semana(self, fecha_inicio):
        fecha_fin = fecha_inicio + timedelta(days=6)
        return SlotDieta.objects.filter(
            usuario=self.usuario,
            fecha__range=[fecha_inicio, fecha_fin]
        ).select_related('comida')

    def get_slot(self, fecha, turno):
        try:
            return SlotDieta.objects.get(
                usuario=self.usuario,
                fecha=fecha,
                turno=turno
            )
        except SlotDieta.DoesNotExist:
            return None

    def asignar(self, fecha, turno, comida_id):
        slot, created = SlotDieta.objects.update_or_create(
            usuario=self.usuario,
            fecha=fecha,
            turno=turno,
            defaults={'comida_id': comida_id}
        )
        return slot

    def quitar(self, fecha, turno):
        SlotDieta.objects.filter(
            usuario=self.usuario,
            fecha=fecha,
            turno=turno
        ).delete()