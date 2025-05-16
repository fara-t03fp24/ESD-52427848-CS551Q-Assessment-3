document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Handle stock filter buttons
    const stockFilterButtons = document.querySelectorAll('[data-stock-filter]');
    stockFilterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('stock', this.dataset.stockFilter);
            window.location.href = currentUrl.toString();
        });
    });

    // Handle chart initialization if Chart.js is available and canvas exists
    if (typeof Chart !== 'undefined') {
        const revenueCanvas = document.getElementById('revenue-chart');
        if (revenueCanvas) {
            new Chart(revenueCanvas, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Monthly Revenue',
                        data: [0, 0, 0, 0, 0, 0], // Replace with actual data
                        borderColor: '#0d6efd',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                drawBorder: false
                            },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value;
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    }

    // Handle confirmation dialogs
    const confirmActions = document.querySelectorAll('[data-confirm]');
    confirmActions.forEach(element => {
        element.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // Handle dynamic status updates
    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const productId = this.dataset.productId;
            const isActive = this.checked;
            
            fetch(`/api/products/${productId}/toggle-status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    is_active: isActive
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success message
                    const toast = new bootstrap.Toast(document.getElementById('statusToast'));
                    document.getElementById('statusToastBody').textContent = 
                        `Product ${isActive ? 'activated' : 'deactivated'} successfully`;
                    toast.show();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.checked = !isActive; // Revert the toggle
            });
        });
    });

    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});