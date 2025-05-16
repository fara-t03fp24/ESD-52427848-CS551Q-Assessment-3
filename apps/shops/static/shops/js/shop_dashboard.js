document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Animate stats cards on load
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Shop selector with enhanced UX
    const shopSelector = document.getElementById('shopSelector');
    if (shopSelector) {
        shopSelector.addEventListener('change', function(e) {
            e.preventDefault();
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
            document.body.appendChild(loadingOverlay);
            
            // Navigate directly to the new shop's dashboard
            window.location.href = `/shops/${this.value}/dashboard/`;
        });
    }

    // Enhanced product search with debounce
    const productSearch = document.getElementById('productSearch');
    const productRows = document.querySelectorAll('tbody tr');
    
    let searchTimeout;
    
    if (productSearch) {
        productSearch.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const searchTerm = this.value.toLowerCase();
                
                productRows.forEach(row => {
                    const productName = row.querySelector('h6').textContent.toLowerCase();
                    const productId = row.querySelector('small').textContent.toLowerCase();
                    
                    if (productName.includes(searchTerm) || productId.includes(searchTerm)) {
                        row.style.display = '';
                        row.style.animation = 'fadeIn 0.5s ease forwards';
                    } else {
                        row.style.animation = 'fadeOut 0.5s ease forwards';
                        setTimeout(() => {
                            row.style.display = 'none';
                        }, 500);
                    }
                });
            }, 300);
        });
    }

    // Enhance filter buttons with smooth transitions
    const stockFilterButtons = document.querySelectorAll('[data-stock-filter]');
    stockFilterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            stockFilterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.stockFilter;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('stock', filter);
            
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
            document.body.appendChild(loadingOverlay);
            
            window.location.href = currentUrl.toString();
        });
    });

    // Enhanced status toggle with animation
    const statusToggles = document.querySelectorAll('.status-toggle');
    statusToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const productId = this.dataset.productId;
            const isActive = this.checked;
            const row = this.closest('tr');
            
            row.style.backgroundColor = 'rgba(13, 110, 253, 0.05)';
            setTimeout(() => {
                row.style.backgroundColor = '';
            }, 1000);
            
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
                    showToast(`Product ${isActive ? 'activated' : 'deactivated'} successfully`, 'success');
                } else {
                    throw new Error('Failed to update status');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.checked = !isActive;
                showToast('Failed to update product status', 'error');
            });
        });
    });

    // Enhanced toast notification
    function showToast(message, type = 'success') {
        const toast = new bootstrap.Toast(document.getElementById('statusToast'));
        const toastBody = document.getElementById('statusToastBody');
        toastBody.textContent = message;
        toastBody.className = `toast-body ${type}`;
        
        const toastEl = document.getElementById('statusToast');
        toastEl.style.animation = 'slideIn 0.3s ease forwards';
        toast.show();
    }

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