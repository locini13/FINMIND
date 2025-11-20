export function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}

// Placeholder for your Chart.js logic
export function updateChart(transactions) {
    // 1. Group transactions by category
    const categories = {};
    transactions.forEach(t => {
        if(t.type === 'expense') {
            categories[t.category] = (categories[t.category] || 0) + t.amount;
        }
    });

    // 2. Update your Chart.js instance
    // Assuming you have a global chart variable or pass it in
    console.log("Updating Graph with:", categories);
    
    // Example:
    // myChart.data.labels = Object.keys(categories);
    // myChart.data.datasets[0].data = Object.values(categories);
    // myChart.update();
}