// static/charts.js
function initializeCandlestickChart(canvasId, historicalData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    try {
        new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: 'Stock Price',
                    data: JSON.parse(historicalData)
                }]
            },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price (₹)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing chart:', error);
    }
}