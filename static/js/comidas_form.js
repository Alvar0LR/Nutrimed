/**
 * comidas_form.js — NutriMed
 * Gestiona la adición y eliminación dinámica de filas de ingredientes
 * en los formularios de crear y editar comida.
 */

function añadirIngrediente() {
  const container = document.getElementById('ingredientes-container');
  if (!container) return;
  const filas = container.querySelectorAll('.ingrediente-row');
  if (filas.length === 0) return;

  const plantilla = filas[0];
  const nuevaFila = plantilla.cloneNode(true);

  const select = nuevaFila.querySelector('select[name="ingrediente_id"]');
  const input  = nuevaFila.querySelector('input[name="cantidad"]');

  if (select) {
    select.selectedIndex = 0;
    const primerOption = select.querySelector('option');
    if (primerOption) primerOption.disabled = false;
  }

  if (input) {
    input.value = '';
  }
 
  const btnQuitar = nuevaFila.querySelector('button[type="button"]');
  if (btnQuitar) {
    btnQuitar.onclick = function () {
      this.closest('.ingrediente-row').remove();
    };
  }

  container.appendChild(nuevaFila);
  
  nuevaFila.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}


document.addEventListener('DOMContentLoaded', function () {
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('button[type="button"]');
    if (!btn) return;

    const fila = btn.closest('.ingrediente-row');
    if (!fila) return;

    const container = document.getElementById('ingredientes-container');
    if (!container) return;

    const filas = container.querySelectorAll('.ingrediente-row');
    if (filas.length <= 1) 
    {
      const select = fila.querySelector('select[name="ingrediente_id"]');
      const input  = fila.querySelector('input[name="cantidad"]');
      if (select) select.selectedIndex = 0;
      if (input)  input.value = '';
      return;
    }
    fila.remove();
  });
});