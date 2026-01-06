if (typeof window._viewManagerLoaded === 'undefined' || !window._viewManagerLoaded) {

    // کلاس اصلی
    class ViewManager {
        constructor() {
            this.isInitialized = false;
            this.currentView = 'table';
            this.resizeTimer = null;
            console.log('ViewManager constructor called');
        }

        init() {
            if (this.isInitialized) {
                console.warn('ViewManager already initialized, skipping...');
                return;
            }

            console.log('View Manager initializing...');

            try {
                this.setupEventListeners();
                this.handleInitialView();
                this.isInitialized = true;
                console.log('View Manager initialized successfully');
            } catch (error) {
                console.error('Error initializing ViewManager:', error);
            }
        }

        setupEventListeners() {
            // مدیریت تغییر سایز صفحه
            window.addEventListener('resize', () => {
                clearTimeout(this.resizeTimer);
                this.resizeTimer = setTimeout(() => {
                    this.handleResponsiveView();
                }, 150);
            });

            // Radio buttons برای تغییر View
            const tableViewRadio = document.getElementById('table-view');
            const cardViewRadio = document.getElementById('card-view');

            if (tableViewRadio) {
                tableViewRadio.addEventListener('change', (e) => {
                    if (e.target.checked && window.innerWidth > 900) {
                        this.switchToView('table');
                    }
                });
            }

            if (cardViewRadio) {
                cardViewRadio.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        this.switchToView('card');
                    }
                });
            }

            // دکمه‌های Select All / Deselect All
            const selectAllBtn = document.getElementById('selectAllBtn');
            const deselectAllBtn = document.getElementById('deselectAllBtn');

            if (selectAllBtn) {
                selectAllBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectAllTickets();
                });
            }

            if (deselectAllBtn) {
                deselectAllBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.deselectAllTickets();
                });
            }
        }

        handleInitialView() {
            const savedView = localStorage.getItem('ticketViewPreference') || 'table';
            this.currentView = savedView;

            if (window.innerWidth <= 900) {
                this.forceMobileView();
            } else {
                this.switchToView(savedView);
            }

            this.updateSelectedCount();
        }

        handleResponsiveView() {
            if (window.innerWidth <= 900) {
                this.forceMobileView();
            } else {
                this.switchToView(this.currentView);
            }
            this.updateSelectedCount();
        }

        switchToView(viewType) {
            if (window.innerWidth <= 900 && viewType === 'table') {
                this.showTempMessage('در صفحه‌های کوچک فقط Card View در دسترس است', 'info');
                return;
            }

            this.currentView = viewType;
            localStorage.setItem('ticketViewPreference', viewType);

            const tableContainer = document.getElementById('table-view-container');
            const cardContainer = document.getElementById('card-view-container');
            const tableRadio = document.getElementById('table-view');
            const cardRadio = document.getElementById('card-view');

            if (viewType === 'table') {
                if (tableContainer) tableContainer.style.display = 'block';
                if (cardContainer) cardContainer.style.display = 'none';
                if (tableRadio) tableRadio.checked = true;
            } else {
                if (tableContainer) tableContainer.style.display = 'none';
                if (cardContainer) cardContainer.style.display = 'block';
                if (cardRadio) cardRadio.checked = true;
            }

            this.updateSelectedCount();
            console.log(`Switched to ${viewType} view`);
        }

        forceMobileView() {
            const tableContainer = document.getElementById('table-view-container');
            const cardContainer = document.getElementById('card-view-container');
            const tableRadio = document.getElementById('table-view');
            const cardRadio = document.getElementById('card-view');

            if (tableContainer) tableContainer.style.display = 'none';
            if (cardContainer) cardContainer.style.display = 'block';
            if (tableRadio) tableRadio.checked = false;
            if (cardRadio) cardRadio.checked = true;

            console.log('Forced to Card View (mobile)');
        }

        selectAllTickets() {
            const isTableView = this.currentView === 'table';
            const formId = isTableView ? 'bulkDeleteForm' : 'cardBulkDeleteForm';
            const selector = isTableView ? 'tr' : '.card';
            const unseenClass = isTableView ? 'table-warning' : 'border-warning';

            const checkboxes = document.querySelectorAll(`#${formId} input[name="selected_tickets"]`);
            checkboxes.forEach(checkbox => {
                const element = checkbox.closest(selector);
                if (element && !element.classList.contains(unseenClass)) {
                    checkbox.checked = true;
                }
            });

            this.updateSelectedCount();
        }

        deselectAllTickets() {
            const formId = this.currentView === 'table' ? 'bulkDeleteForm' : 'cardBulkDeleteForm';
            const checkboxes = document.querySelectorAll(`#${formId} input[name="selected_tickets"]`);
            checkboxes.forEach(checkbox => checkbox.checked = false);
            this.updateSelectedCount();
        }

        updateSelectedCount() {
            const formId = this.currentView === 'table' ? 'bulkDeleteForm' : 'cardBulkDeleteForm';
            const selectedCount = document.querySelectorAll(`#${formId} input[name="selected_tickets"]:checked`).length;

            const badge = document.getElementById('selectedCountBadge');
            const countSpan = document.getElementById('selectedCount');

            if (countSpan) countSpan.textContent = selectedCount;
            if (badge) badge.style.display = selectedCount > 0 ? 'inline-block' : 'none';

            console.log('Selected count:', selectedCount);
            return selectedCount;
        }

        showTempMessage(message, type = 'info') {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            document.body.appendChild(alertDiv);

            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 3000);
        }
    }

    // ایجاد instance و علامت گذاری به عنوان لود شده
    if (!window.viewManager) {
        window.viewManager = new ViewManager();
        window._viewManagerLoaded = true;

        // Initialization
        document.addEventListener('DOMContentLoaded', function() {
            if (window.viewManager && !window.viewManager.isInitialized) {
                window.viewManager.init();
            }
        });
    } else {
        console.warn('viewManager already exists, skipping creation');
    }

} else {
    console.warn('view-manager.js already loaded, skipping...');
}