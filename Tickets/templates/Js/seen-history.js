document.addEventListener('DOMContentLoaded', function () {
    // CSRF Token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log('seen-history.js loaded - Debug mode');

    // 1. رویداد برای دکمه‌های Mark as Seen
    document.querySelectorAll('.mark-seen-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const ticketId = this.dataset.ticketId;
            console.log('Mark as Seen clicked (from seen-history.js):', ticketId);
            markTicketAsSeen(ticketId, this);
        });
    });

    // 2. رویداد برای دکمه‌های مشاهده تاریخچه
    document.querySelectorAll('.seen-history-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const ticketId = this.dataset.ticketId;
            console.log('Seen History clicked:', ticketId);
            showSeenHistory(ticketId);
        });
    });

    // 3. تابع mark as seen
    function markTicketAsSeen(ticketId, buttonElement) {
        buttonElement.disabled = true;
        const originalHtml = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Processing...';

        fetch(`/ticket/${ticketId}/seen/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
            .then(response => {
                console.log('Mark as Seen response status:', response.status);
                if (response.status === 403) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'You do not have permission to mark this ticket as seen.');
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Mark as Seen response data:', data);
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                    buttonElement.disabled = false;
                    buttonElement.innerHTML = originalHtml;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || 'An error occurred. Please try again.');
                buttonElement.disabled = false;
                buttonElement.innerHTML = originalHtml;
            });
    }

    // 4. تابع نمایش تاریخچه
    function showSeenHistory(ticketId) {
        console.log('Showing seen history for ticket:', ticketId);

        // ایجاد modal داینامیک
        const modalHtml = `
            <div class="modal fade" id="seenHistoryModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Seen History</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center py-4">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p class="mt-2 text-muted">Loading history...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // اضافه کردن modal به صفحه
        if (!document.getElementById('seenHistoryModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        // نمایش modal
        const modal = new bootstrap.Modal(document.getElementById('seenHistoryModal'));
        modal.show();

        // درخواست AJAX برای گرفتن تاریخچه
        fetch(`/ticket/${ticketId}/seen-details/`, {
            headers: {
                'X-CSRFToken': csrftoken,
            }
        })
            .then(response => {
                console.log('Seen History response status:', response.status);
                if (response.status === 403) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'You do not have permission to view this history.');
                    });
                }
                return response.json();
            })
            .then(data => {
                const modalBody = document.querySelector('#seenHistoryModal .modal-body');
                console.log('Seen History data:', data);

                if (data.success) {
                    let html = `
                    <div class="mb-3">
                        <h6>Ticket #${data.ticket.tracking_code}</h6>
                        <p class="text-muted mb-1">${data.ticket.subject}</p>
                        <p class="mb-0">
                            <span class="badge bg-info">
                                Total seen: ${data.ticket.total_seen_count} times
                            </span>
                        </p>
                    </div>
                    <hr>
                `;

                    if (data.history.length > 0) {
                        html += '<div class="list-group">';
                        data.history.forEach(item => {
                            html += `
                            <div class="list-group-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>${item.user.full_name}</strong>
                                        <div class="text-muted small">${item.user.username}</div>
                                    </div>
                                    <div class="text-end">
                                        <div class="text-primary">${item.seen_at_relative}</div>
                                        <div class="text-muted small">${item.seen_at}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                        });
                        html += '</div>';
                    } else {
                        html += '<p class="text-center text-muted py-3">No seen history available.</p>';
                    }

                    modalBody.innerHTML = html;
                } else {
                    modalBody.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        ${data.error || 'Failed to load history.'}
                    </div>
                `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const modalBody = document.querySelector('#seenHistoryModal .modal-body');
                modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${error.message || 'An error occurred while loading history.'}
                </div>
            `;
            });
    }
});
