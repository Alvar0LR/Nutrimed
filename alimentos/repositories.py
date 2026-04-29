from .models import Alimentos, Comida, ComidaIngrediente, SlotDieta
from datetime import date, timedelta

class AlimentoRepository:
    def __init__(self, usuario):
        self.usuario = usuario

    def get_all(self):
        return Alimentos.objects.filter(usuario=self.usuario)

    def get_by_grupo(self, grupo):
        return Alimentos.objects.filter(usuario=self.usuario, grupo=grupo)

    def get_by_id(self, id):
        return Alimentos.objects.get(id=id, usuario=self.usuario)

    def buscar(self, query):
        return Alimentos.objects.filter(usuario=self.usuario, nombre__icontains=query)

    def create(self, data):
        return Alimentos.objects.create(usuario=self.usuario, **data)

    def update(self, id, data):
        alimento = self.get_by_id(id)
        for key, value in data.items():
            setattr(alimento, key, value)
        alimento.save()
        return alimento

    def delete(self, id):
        alimento = self.get_by_id(id)
        alimento.delete()
    
    def contar(self):
        return Alimentos.objects.filter(usuario=self.usuario).count()

class ComidaRepository:
    def __init__(self, usuario):
        self.usuario = usuario

    def get_all(self):
        return Comida.objects.filter(usuario=self.usuario)

    def get_by_name(self, query):
        return Comida.objects.filter(usuario=self.usuario, nombre__icontains=query)

    def get_by_id(self, id):
        return Comida.objects.get(id=id, usuario=self.usuario)

    def create(self, nombre, turno):
        return Comida.objects.create(usuario=self.usuario, nombre=nombre, turno=turno)

    def add_ingrediente(self, comida, alimento_id, cantidad):
        return ComidaIngrediente.objects.create(
            comida=comida,
            alimento_id=alimento_id,
            cantidad=cantidad
        )

    def delete(self, id):
        comida = self.get_by_id(id)
        comida.delete()
    
    def update(self, id, nombre, turno):
        comida = self.get_by_id(id)
        comida.nombre = nombre
        comida.turno = turno
        comida.save()
        return comida

    def update_ingredientes(self, comida, ingrediente_ids, cantidades):
        comida.comidaingrediente_set.all().delete()
        for ing_id, cantidad in zip(ingrediente_ids, cantidades):
            if ing_id and cantidad:
                self.add_ingrediente(comida, ing_id, cantidad)


    def get_with_ingredientes(self, id):
        comida = self.get_by_id(id)
        ingredientes = comida.comidaingrediente_set.select_related('alimento').all()
        return comida, ingredientes

    def calcular_macros(self, id):
        comida = self.get_by_id(id)
        return comida.calcular_macros()

    def contar(self):
        return Comida.objects.filter(usuario=self.usuario).count()
    


class SlotDietaRepository:

    def __init__(self, usuario):
        self.usuario = usuario

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