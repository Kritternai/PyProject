/**
 * Toast Notification System
 * Professional toast notifications for user feedback
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info'
        };

        toast.innerHTML = `
            <div class="toast-icon">
                <i class="bi ${icons[type]}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${titles[type]}</div>
                <p class="toast-message">${message}</p>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;

        this.container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.classList.add('removing');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return toast;
    }

    success(message, duration = 3000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 4000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 3500) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }
}

/**
 * Confirm Dialog System
 * Modern confirm dialogs replacing browser alerts
 */

class ConfirmDialog {
    constructor() {
        this.overlay = null;
    }

    show(options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Confirm Action',
                message = 'Are you sure you want to proceed?',
                type = 'warning', // warning, danger, info
                confirmText = 'Confirm',
                cancelText = 'Cancel',
                confirmClass = 'primary'
            } = options;

            // Create overlay
            this.overlay = document.createElement('div');
            this.overlay.className = 'confirm-overlay';

            const icons = {
                warning: 'bi-exclamation-triangle',
                danger: 'bi-trash',
                info: 'bi-info-circle'
            };

            this.overlay.innerHTML = `
                <div class="confirm-dialog">
                    <div class="confirm-header">
                        <div class="confirm-icon ${type}">
                            <i class="bi ${icons[type]}"></i>
                        </div>
                        <h3 class="confirm-title">${title}</h3>
                    </div>
                    <p class="confirm-message">${message}</p>
                    <div class="confirm-actions">
                        <button class="confirm-btn confirm-btn-cancel" data-action="cancel">
                            ${cancelText}
                        </button>
                        <button class="confirm-btn confirm-btn-confirm ${confirmClass}" data-action="confirm">
                            ${confirmText}
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(this.overlay);

            // Handle button clicks
            this.overlay.querySelectorAll('.confirm-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const action = btn.dataset.action;
                    this.close();
                    resolve(action === 'confirm');
                });
            });

            // Close on overlay click
            this.overlay.addEventListener('click', (e) => {
                if (e.target === this.overlay) {
                    this.close();
                    resolve(false);
                }
            });
        });
    }

    close() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }

    async confirm(message, title = 'Confirm') {
        return this.show({
            title,
            message,
            type: 'warning',
            confirmText: 'Confirm',
            confirmClass: 'primary'
        });
    }

    async delete(message = 'This action cannot be undone.', title = 'Delete Item') {
        return this.show({
            title,
            message,
            type: 'danger',
            confirmText: 'Delete',
            confirmClass: ''
        });
    }
}

/**
 * Loading Overlay
 * Full screen loading indicator
 */

class LoadingOverlay {
    constructor() {
        this.overlay = null;
        this.count = 0;
    }

    show() {
        this.count++;
        
        if (!this.overlay) {
            this.overlay = document.createElement('div');
            this.overlay.className = 'loading-overlay';
            this.overlay.innerHTML = '<div class="loading-spinner"></div>';
            document.body.appendChild(this.overlay);
        }
    }

    hide() {
        this.count = Math.max(0, this.count - 1);
        
        if (this.count === 0 && this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }

    hideAll() {
        this.count = 0;
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }
}

// Create global instances
const toast = new ToastNotification();
const confirmDialog = new ConfirmDialog();
const loading = new LoadingOverlay();

// Export for use in other scripts
window.toast = toast;
window.confirmDialog = confirmDialog;
window.loading = loading;

// Convenience functions
window.showToast = (message, type = 'info') => toast.show(message, type);
window.showSuccess = (message) => toast.success(message);
window.showError = (message) => toast.error(message);
window.showWarning = (message) => toast.warning(message);
window.showInfo = (message) => toast.info(message);
window.showLoading = () => loading.show();
window.hideLoading = () => loading.hide();
window.confirmAction = (message, title) => confirmDialog.confirm(message, title);
window.confirmDelete = (message, title) => confirmDialog.delete(message, title);

