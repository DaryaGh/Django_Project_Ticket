document.addEventListener('DOMContentLoaded', function () {
    // CSRF Token برای AJAX
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // رویداد کلیک روی دکمه‌های Mark as Seen
    document.querySelectorAll('.mark-seen-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const ticketId = this.dataset.ticketId;

            // درخواست AJAX برای mark as seen
            fetch(`/ticket/${ticketId}/seen/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // رفرش صفحه
                        location.reload();
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred. Please try again.');
                });
        });
    });

    // رویداد کلیک روی وضعیت Seen برای نمایش جزئیات
    document.querySelectorAll('.seen-status-cell').forEach(cell => {
        cell.addEventListener('click', function () {
            const ticketId = this.dataset.ticketId;
            showSeenDetails(ticketId);
        });
    });

    // تابع نمایش جزئیات Seen
    function showSeenDetails(ticketId) {
        fetch(`/ticket/${ticketId}/seen-details/`)
            .then(response => response.text())
            .then(html => {
                document.getElementById('seenDetailsContent').innerHTML = html;
                const modal = new bootstrap.Modal(document.getElementById('seenDetailsModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Highlight تیکت‌های unseen
    const unseenRows = document.querySelectorAll('tr.table-warning');
    unseenRows.forEach(row => {
        row.addEventListener('mouseenter', function () {
            this.classList.add('table-active');
        });
        row.addEventListener('mouseleave', function () {
            this.classList.remove('table-active');
        });
    });
});
