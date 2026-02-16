// مدیریت دکمه‌های Mark as Seen
document.addEventListener('DOMContentLoaded', function() {
    // دکمه‌های Mark as Seen
    document.querySelectorAll('.mark-seen-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const ticketId = this.dataset.ticketId;
            const button = this;

            // تغییر حالت دکمه به loading
            const originalText = button.innerHTML;
            button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
            button.disabled = true;

            // ارسال درخواست AJAX
            fetch(`/ticket/${ticketId}/mark-seen/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // نمایش پیام موفقیت
                    showToast('تیکت با موفقیت علامت‌گذاری شد', 'success');

                    // حذف هایلایت warning از ردیف
                    const row = button.closest('tr');
                    if (row && row.classList.contains('table-warning')) {
                        row.classList.remove('table-warning');
                        row.classList.add('table-success');

                        // حذف badge "New"
                        const newBadge = row.querySelector('.badge.bg-danger');
                        if (newBadge) newBadge.remove();

                        // تغییر وضعیت دکمه
                        button.innerHTML = '<i class="bi bi-eye-fill"></i> Seen';
                        button.classList.remove('btn-outline-info');
                        button.classList.add('btn-success');
                    }

                    // رفرش صفحه بعد از 2 ثانیه
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    showToast(data.message, 'danger');
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('خطا در ارتباط با سرور', 'danger');
                button.innerHTML = originalText;
                button.disabled = false;
            });
        });
    });

    // دکمه‌های نمایش تاریخچه
    document.querySelectorAll('.seen-history-btn').forEach(button => {
        button.addEventListener('click', function() {
            const ticketId = this.dataset.ticketId;
            loadSeenHistory(ticketId);
        });
    });

    // تابع برای دریافت تاریخچه
    function loadSeenHistory(ticketId) {
        const content = document.getElementById('seenHistoryContent');
        content.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">در حال بارگذاری تاریخچه...</p>
            </div>
        `;

        fetch(`/ticket/${ticketId}/seen-history/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let html = `
                    <h6 class="mb-3">تاریخچه دیده شدن تیکت #${data.ticket_code}</h6>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>کاربر</th>
                                    <th>نقش</th>
                                    <th>تاریخ مشاهده</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                if (data.seen_history.length === 0) {
                    html += `
                        <tr>
                            <td colspan="3" class="text-center py-3 text-muted">
                                هنوز کسی این تیکت را ندیده است
                            </td>
                        </tr>
                    `;
                } else {
                    data.seen_history.forEach(item => {
                        html += `
                            <tr>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="avatar-sm bg-light rounded-circle d-flex align-items-center justify-content-center me-2">
                                            <i class="bi bi-person text-dark"></i>
                                        </div>
                                        <div>
                                            <strong>${item.user.full_name || item.user.username}</strong><br>
                                            <small class="text-muted">${item.user.username}</small>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span class="badge bg-info">${item.role}</span>
                                </td>
                                <td>
                                    ${item.seen_at_display}<br>
                                    <small class="text-muted">
                                        ${timeSince(new Date(item.seen_at))} پیش
                                    </small>
                                </td>
                            </tr>
                        `;
                    });
                }

                html += `
                            </tbody>
                        </table>
                    </div>
                    <div class="alert alert-info mt-3">
                        <i class="bi bi-info-circle me-2"></i>
                        تعداد کل مشاهده‌ها: <strong>${data.total_views}</strong>
                    </div>
                `;

                content.innerHTML = html;
            } else {
                content.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        ${data.message}
                    </div>
                `;
            }
        })
        .catch(error => {
            content.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    خطا در دریافت اطلاعات
                </div>
            `;
        });
    }

    // Helper functions
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

    function showToast(message, type = 'info') {
        // کد نمایش toast با Bootstrap
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        const container = document.getElementById('toastContainer') || createToastContainer();
        container.innerHTML += toastHtml;

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        setTimeout(() => {
            toastElement.remove();
        }, 5000);
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(container);
        return container;
    }

    function timeSince(date) {
        const seconds = Math.floor((new Date() - date) / 1000);

        let interval = seconds / 31536000;
        if (interval > 1) return Math.floor(interval) + " سال";

        interval = seconds / 2592000;
        if (interval > 1) return Math.floor(interval) + " ماه";

        interval = seconds / 86400;
        if (interval > 1) return Math.floor(interval) + " روز";

        interval = seconds / 3600;
        if (interval > 1) return Math.floor(interval) + " ساعت";

        interval = seconds / 60;
        if (interval > 1) return Math.floor(interval) + " دقیقه";

        return Math.floor(seconds) + " ثانیه";
    }
});