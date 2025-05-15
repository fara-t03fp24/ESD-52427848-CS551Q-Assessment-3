document.addEventListener('DOMContentLoaded', function() {
    // Initialize revenue chart
    const revenueCtx = document.getElementById('revenue-chart');
    if (revenueCtx) {
        const revenueData = JSON.parse(revenueCtx.dataset.revenue || '[]');
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: revenueData.map(d => new Date(d.month).toLocaleDateString('default', { month: 'short', year: 'numeric' })),
                datasets: [{
                    label: 'Monthly Revenue',
                    data: revenueData.map(d => d.revenue),
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `$${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }

    // Handle product filter buttons
    const productFilters = document.querySelectorAll('[data-product-filter]');
    productFilters.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const filter = this.dataset.productFilter;
            const url = new URL(window.location);
            url.searchParams.set('stock', filter);
            window.location = url;
        });
    });

    // Handle funds period buttons
    const fundsPeriodButtons = document.querySelectorAll('[data-funds-period]');
    fundsPeriodButtons.forEach(button => {
        button.addEventListener('click', function() {
            fundsPeriodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            // Update revenue chart based on selected period
            // This will be implemented with AJAX calls to fetch data
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});