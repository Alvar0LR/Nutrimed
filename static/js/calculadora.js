const modalEliminar = document.getElementById('modalEliminar')
modalEliminar.addEventListener('show.bs.modal', function (event) {
  const btn = event.relatedTarget
  const id = btn.getAttribute('data-id')
  const fecha = btn.getAttribute('data-fecha')
  const get = btn.getAttribute('data-get')

  document.getElementById('modalFecha').textContent = fecha
  document.getElementById('modalGet').textContent = get + ' kcal'
  document.getElementById('formEliminar').action = '/calculadora/eliminar/' + id + '/'
})