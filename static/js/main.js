
/* ============================================ */
/* static/js/main.js - ASOSIY JAVASCRIPT */
/* ============================================ */

// Main JavaScript for ERP Sistema
console.log('ERP Sistema - Main JS Loaded');

// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getInstanceOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Haqiqatan ham o\'chirmoqchimisiz? Bu amalni qaytarib bo\'lmaydi!')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Form validation helper
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Tooltips initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers initialization
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Helper function: Show loading spinner
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Yuklanmoqda...';
    element.disabled = true;
    return originalContent;
}

// Helper function: Hide loading spinner
function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Helper function: Format number
function formatNumber(num) {
    return new Intl.NumberFormat('uz-UZ').format(num);
}

// Helper function: Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Nusxalandi!');
    }).catch(function(err) {
        console.error('Nusxalash xatosi:', err);
    });
}