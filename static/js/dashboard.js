const ctx = document.getElementById('grafica-calorias').getContext('2d');

new Chart(ctx, {
  type: 'bar',
  data: {
    labels: window.dashboardLabels,
    datasets: [{
      label: 'Calorías',
      data: window.dashboardDatos,
      backgroundColor: '#9FE1CB',
      borderColor: '#0F6E56',
      borderWidth: 1,
      borderRadius: 4,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, grid: { color: '#f0f0f0' } },
      x: { grid: { display: false } }
    }
  }
});