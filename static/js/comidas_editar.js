function añadirIngrediente() {
  const container = document.getElementById('ingredientes-container')
  const primera = container.querySelector('.ingrediente-row')
  const nueva = primera.cloneNode(true)
  nueva.querySelector('select').value = ''
  nueva.querySelector('input').value = ''
  container.appendChild(nueva)
}