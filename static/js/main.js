// Main JavaScript file for Attendance System

// Smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';

// Auto-hide alerts after 5 seconds with fade out
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 500);
        }, 5000);
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Real-time clock
    updateClock();
    setInterval(updateClock, 1000);

    // Mark notifications as read when clicked
    const notificationItems = document.querySelectorAll('.notification-item.unread');
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            this.classList.remove('unread');
            this.style.transition = 'all 0.3s ease';
        });
    });

    // Add hover effect to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});

// Update clock function
function updateClock() {
    const clockElement = document.getElementById('live-clock');
    if (clockElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
        clockElement.textContent = timeString;
    }
}

// Confirm before check-out
function confirmCheckOut() {
    return confirm('Are you sure you want to check out?');
}

// Confirm before starting break
function confirmBreak(breakType) {
    return confirm(`Start ${breakType} break?`);
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let row of rows) {
        const cols = row.querySelectorAll('td, th');
        let csvRow = [];
        for (let col of cols) {
            csvRow.push(col.innerText);
        }
        csv.push(csvRow.join(','));
    }
    
    downloadCSV(csv.join('\n'), filename);
}

// Download CSV file
function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Show loading spinner
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading"></span> Loading...';
    button.disabled = true;
    return originalText;
}

// Hide loading spinner
function hideLoading(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}

// AJAX form submission
function submitFormAjax(formId, successCallback) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = showLoading(submitButton);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoading(submitButton, originalText);
            if (data.success) {
                showAlert('success', data.message);
                if (successCallback) successCallback(data);
            } else {
                showAlert('danger', data.message || 'An error occurred');
            }
        })
        .catch(error => {
            hideLoading(submitButton, originalText);
            showAlert('danger', 'Network error. Please try again.');
            console.error('Error:', error);
        });
    });
}

// Show alert message
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show animate__animated animate__fadeInDown`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container, .container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Format time duration
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}

// Calculate work hours
function calculateWorkHours(checkIn, checkOut) {
    if (!checkIn || !checkOut) return '0h 0m';
    
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    const diff = end - start;
    const minutes = Math.floor(diff / 60000);
    
    return formatDuration(minutes);
}

// Validate date range
function validateDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    if (end < start) {
        showAlert('warning', 'End date cannot be before start date');
        return false;
    }
    
    return true;
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('input', debounce(function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const tableRows = document.querySelectorAll('tbody tr');
        
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }, 300));
}

// Print functionality
function printPage() {
    window.print();
}

// Refresh page data
function refreshData() {
    location.reload();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('success', 'Copied to clipboard!');
    }).catch(err => {
        showAlert('danger', 'Failed to copy');
        console.error('Copy error:', err);
    });
}

// Check browser notifications permission
function checkNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Show browser notification
function showNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/static/images/logo.png'
        });
    }
}

// Initialize on page load
checkNotificationPermission();

// Service Worker for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to enable service worker
        // navigator.serviceWorker.register('/static/js/sw.js');
    });
}


// ===================================
// SYSTEM MODAL - Custom Alert & Confirm
// Replaces browser alert() and confirm()
// ===================================

/**
 * Show a custom system alert modal (replaces browser alert)
 * @param {string} message - The message to display
 * @param {string} type - 'success', 'error', 'warning', 'info' (default: auto-detect)
 * @param {string} title - Optional custom title
 * @returns {Promise} - Resolves when user clicks OK
 */
function systemAlert(message, type, title) {
    return new Promise((resolve) => {
        // Auto-detect type from message content
        if (!type) {
            if (message.toLowerCase().includes('error') || message.toLowerCase().includes('failed')) {
                type = 'error';
            } else if (message.toLowerCase().includes('success') || message.toLowerCase().includes('successfully')) {
                type = 'success';
            } else if (message.toLowerCase().includes('warning')) {
                type = 'warning';
            } else {
                type = 'info';
            }
        }

        const modal = document.getElementById('systemAlertModal');
        const iconEl = document.getElementById('systemAlertIcon');
        const titleEl = document.getElementById('systemAlertTitle');
        const messageEl = document.getElementById('systemAlertMessage');
        const okBtn = document.getElementById('systemAlertOkBtn');

        // Set icon and colors based on type
        const config = {
            success: { icon: 'fa-check-circle', class: '', title: 'Success', btnClass: 'btn-success' },
            error: { icon: 'fa-times-circle', class: 'error-icon', title: 'Error', btnClass: 'btn-danger' },
            warning: { icon: 'fa-exclamation-triangle', class: 'warning-icon', title: 'Warning', btnClass: 'btn-warning' },
            info: { icon: 'fa-info-circle', class: 'info-icon', title: 'Information', btnClass: 'btn-primary' }
        };

        const cfg = config[type] || config.info;

        iconEl.className = 'system-modal-icon ' + cfg.class;
        iconEl.innerHTML = `<i class="fas ${cfg.icon}"></i>`;
        titleEl.textContent = title || cfg.title;
        messageEl.textContent = message;

        // Reset button classes
        okBtn.className = 'btn ' + cfg.btnClass;

        // Show modal
        const bsModal = new bootstrap.Modal(modal, { backdrop: 'static' });
        bsModal.show();

        // Handle OK click
        function handleOk() {
            bsModal.hide();
            okBtn.removeEventListener('click', handleOk);
            modal.removeEventListener('hidden.bs.modal', handleHidden);
            resolve(true);
        }

        function handleHidden() {
            okBtn.removeEventListener('click', handleOk);
            modal.removeEventListener('hidden.bs.modal', handleHidden);
            resolve(true);
        }

        okBtn.addEventListener('click', handleOk);
        modal.addEventListener('hidden.bs.modal', handleHidden);
    });
}

/**
 * Show a custom system confirm modal (replaces browser confirm)
 * @param {string} message - The message to display
 * @param {object} options - Optional settings { title, confirmText, cancelText, type }
 * @returns {Promise<boolean>} - Resolves true if confirmed, false if cancelled
 */
function systemConfirm(message, options = {}) {
    return new Promise((resolve) => {
        const modal = document.getElementById('systemConfirmModal');
        const titleEl = document.getElementById('systemConfirmTitle');
        const messageEl = document.getElementById('systemConfirmMessage');
        const okBtn = document.getElementById('systemConfirmOkBtn');
        const cancelBtn = document.getElementById('systemConfirmCancelBtn');

        titleEl.textContent = options.title || 'Confirm Action';
        messageEl.textContent = message;

        // Customize buttons
        if (options.confirmText) {
            okBtn.innerHTML = `<i class="fas fa-check me-1"></i>${options.confirmText}`;
        } else {
            okBtn.innerHTML = '<i class="fas fa-check me-1"></i>Confirm';
        }

        if (options.cancelText) {
            cancelBtn.innerHTML = `<i class="fas fa-times me-1"></i>${options.cancelText}`;
        } else {
            cancelBtn.innerHTML = '<i class="fas fa-times me-1"></i>Cancel';
        }

        // Set button type/color
        if (options.type === 'danger') {
            okBtn.className = 'btn btn-danger';
        } else if (options.type === 'warning') {
            okBtn.className = 'btn btn-warning';
        } else {
            okBtn.className = 'btn btn-primary';
        }

        // Show modal
        const bsModal = new bootstrap.Modal(modal, { backdrop: 'static' });
        bsModal.show();

        let resolved = false;

        function handleConfirm() {
            if (resolved) return;
            resolved = true;
            bsModal.hide();
            cleanup();
            resolve(true);
        }

        function handleCancel() {
            if (resolved) return;
            resolved = true;
            bsModal.hide();
            cleanup();
            resolve(false);
        }

        function handleHidden() {
            if (resolved) return;
            resolved = true;
            cleanup();
            resolve(false);
        }

        function cleanup() {
            okBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
            modal.removeEventListener('hidden.bs.modal', handleHidden);
        }

        okBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
        modal.addEventListener('hidden.bs.modal', handleHidden);
    });
}

// Override native alert and confirm globally
window._originalAlert = window.alert;
window._originalConfirm = window.confirm;

window.alert = function(message) {
    systemAlert(message);
};

window.confirm = function(message) {
    // Since confirm needs to be synchronous but our modal is async,
    // we can't directly override it for synchronous code.
    // Instead, we provide systemConfirm for async usage.
    // For backward compatibility with existing code that uses confirm() in if statements,
    // we'll use a workaround with a blocking approach.
    // NOTE: This won't work for synchronous confirm() calls.
    // Those need to be refactored to use systemConfirm() with async/await.
    return window._originalConfirm(message);
};
