from .models import Alimentos

def __init__(self, usuario):
    self.usuario = usuario

def get_all(self):
    return Alimentos.objects.filter(usuario=self.usuario)

def get_by_grupo(self, grupo):
    return Alimentos.objects.filter(usuario=self.usuario, grupo=grupo)

def get_by_id(self, id):
    return Alimentos.objects.get(id=id, usuario=self.usuario)

def buscar(self, query):
    return Alimentos.objects.filter(usuario=self.usuario, nombre_icontains=query)

def create(self, data):
    return Alimentos.objects.create(usuario=self.usuario, **data)

def update(self, id, data):
    alimento = self.get_by_id(id)
    for key, value in data.item():
        setattr(alimento, key, value)
    alimento.save()
    return alimento

def delete(self, id):
    alimento = self.get_by_id(id)
    alimento.delete()