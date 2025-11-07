// Gestionnaire d'interface utilisateur
class UIManager {
    constructor() {
        this.notificationContainer = this.createNotificationContainer();
        this.loadingOverlay = this.createLoadingOverlay();
    }

    createNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        return container;
    }

    createLoadingOverlay() {
        let overlay = document.getElementById('global-loading');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'global-loading';
            overlay.className = 'modal';
            overlay.innerHTML = `
                <div class="modal-content" style="max-width: 200px;">
                    <div class="modal-body" style="text-align: center;">
                        <div class="loading" style="width: 2rem; height: 2rem; margin: 0 auto 1rem;"></div>
                        <p id="loading-message">Chargement...</p>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    showLoading(message = 'Chargement...') {
        const messageEl = this.loadingOverlay.querySelector('#loading-message');
        if (messageEl) {
            messageEl.textContent = message;
        }
        this.loadingOverlay.classList.add('active');
    }

    hideLoading() {
        this.loadingOverlay.classList.remove('active');
    }

    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-triangle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${icons[type] || 'fa-info-circle'}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        this.notificationContainer.appendChild(notification);

        // Animation d'entrée
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.dismissNotification(notification);
            }, duration);
        }

        return notification;
    }

    dismissNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }

    showError(message, details = '') {
        let fullMessage = message;
        if (details) {
            fullMessage += `<br><small>${details}</small>`;
        }
        return this.showNotification(fullMessage, 'error', 8000);
    }

    showSuccess(message) {
        return this.showNotification(message, 'success', 3000);
    }

    showWarning(message) {
        return this.showNotification(message, 'warning', 5000);
    }

    showInfo(message) {
        return this.showNotification(message, 'info', 4000);
    }

    confirmAction(message, confirmText = 'Confirmer', cancelText = 'Annuler') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 400px;">
                    <div class="modal-header">
                        <h3 class="modal-title">Confirmation</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-outline" id="confirm-cancel">${cancelText}</button>
                        <button class="btn btn-primary" id="confirm-ok">${confirmText}</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            const closeModal = () => {
                modal.remove();
            };

            modal.querySelector('#confirm-ok').onclick = () => {
                closeModal();
                resolve(true);
            };

            modal.querySelector('#confirm-cancel').onclick = () => {
                closeModal();
                resolve(false);
            };

            modal.querySelector('.modal-close').onclick = () => {
                closeModal();
                resolve(false);
            };

            modal.onclick = (e) => {
                if (e.target === modal) {
                    closeModal();
                    resolve(false);
                }
            };
        });
    }

    updateMetric(selector, value, formatter = null) {
        const element = document.querySelector(selector);
        if (element) {
            const newValue = formatter ? formatter(value) : value;
            if (element.textContent !== newValue) {
                element.textContent = newValue;
                element.classList.add('metric-update');
                setTimeout(() => {
                    element.classList.remove('metric-update');
                }, 500);
            }
        }
    }

    enableElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.disabled = false;
        }
    }

    disableElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.disabled = true;
        }
    }

    showElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.style.display = '';
        }
    }

    hideElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.style.display = 'none';
        }
    }
}

// Styles pour les notifications
const notificationStyles = `
<style>
.notification-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 10000;
    max-width: 400px;
}

.notification {
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    margin-bottom: 0.5rem;
    transform: translateX(100%);
    opacity: 0;
    transition: all 0.3s ease;
    border-left: 4px solid #3b82f6;
}

.notification.show {
    transform: translateX(0);
    opacity: 1;
}

.notification-success {
    border-left-color: #10b981;
}

.notification-error {
    border-left-color: #ef4444;
}

.notification-warning {
    border-left-color: #f59e0b;
}

.notification-info {
    border-left-color: #3b82f6;
}

.notification-content {
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.notification-content i {
    font-size: 1.25rem;
}

.notification-success i { color: #10b981; }
.notification-error i { color: #ef4444; }
.notification-warning i { color: #f59e0b; }
.notification-info i { color: #3b82f6; }

.notification-close {
    background: none;
    border: none;
    color: #6b7280;
    cursor: pointer;
    margin-left: auto;
    padding: 0.25rem;
}

.notification-close:hover {
    color: #374151;
}

@media (max-width: 768px) {
    .notification-container {
        left: 1rem;
        right: 1rem;
        max-width: none;
    }
}
</style>
`;

// Ajouter les styles au document
document.head.insertAdjacentHTML('beforeend', notificationStyles);