// static/dashboard.js
// Fetch and update live prices
function updateStockPrices() {
    const stockRows = document.querySelectorAll('.stock-row');
    stockRows.forEach(row => {
        const symbol = row.dataset.symbol;
        fetch(`/api/stock/${symbol}/price`)
            .then(response => response.json())
            .then(data => {
                if (data.price) {
                    const tokenPrice = data.price / 100; // Assuming token_count=100
                    row.querySelector('.stock-price').textContent = `₹${data.price.toFixed(2)}`;
                    row.querySelector('.token-price').textContent = `₹${tokenPrice.toFixed(2)}`;
                }
            })
            .catch(error => console.error(`Error fetching price for ${symbol}:`, error));
    });
}

// Run price updates every 60 seconds
document.addEventListener('DOMContentLoaded', () => {
    updateStockPrices();
    setInterval(updateStockPrices, 60000);
});