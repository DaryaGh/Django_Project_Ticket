// تابع سوییچ بین حالت‌ها
function switchView(mode) {
    const tableView = document.getElementById('table-view-container');
    const cardView = document.getElementById('card-view-container');

    if (mode === 'table') {
        tableView.style.display = 'block';
        cardView.style.display = 'none';
        // ذخیره در localStorage
        localStorage.setItem('preferredView', 'table');
    } else {
        tableView.style.display = 'none';
        cardView.style.display = 'block';
        // ذخیره در localStorage
        localStorage.setItem('preferredView', 'card');
    }

    // به روزرسانی tooltip‌ها
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// بارگذاری حالت ترجیحی کاربر
document.addEventListener('DOMContentLoaded', function () {
    const preferredView = localStorage.getItem('preferredView') || 'table';

    // تنظیم radio button مناسب
    if (preferredView === 'card') {
        document.getElementById('card-view').checked = true;
        document.getElementById('table-view').checked = false;
    } else {
        document.getElementById('table-view').checked = true;
        document.getElementById('card-view').checked = false;
    }

    // سوییچ به حالت ترجیحی
    switchView(preferredView);
});


