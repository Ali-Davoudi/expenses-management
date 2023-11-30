/**
 * ChartJS
 */

document.addEventListener('DOMContentLoaded', function () {
  const renderChart = (data, labels) => {
    const ctx = document.getElementById('myChart');

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          label: 'Last 6 months expenses',
          data: data,
          borderWidth: 1
        }]
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: 'Expenses per category'
          }
        }
      }
    });
  }

  const getChartData = () => {
    fetch('/expense-cat-sum').then(res => res.json()).then(result => {
      console.log('result: ', result)
      const categoryExpenseData = result.expense_category_data

      const [labels, data] = [
        Object.keys(categoryExpenseData),
        Object.values(categoryExpenseData),
      ]

      renderChart(data, labels)
    })
  }

  getChartData();
});
