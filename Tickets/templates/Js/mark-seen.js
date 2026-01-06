document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log('mark-seen.js loaded - Debug mode');

    document.querySelectorAll('.mark-seen-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const ticketId = this.dataset.ticketId;
            const button = this;

            console.log('Mark as Seen clicked for ticket:', ticketId);
            console.log('Button:', button);

            // نمایش loading state
            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Processing...';

            // درخواست AJAX برای mark as seen
            fetch(`/ticket/${ticketId}/seen/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            })
            .then(response => {
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);

                if (response.status === 403) {
                    // اگر دسترسی نداری
                    return response.json().then(data => {
                        console.log('403 Error data:', data);
                        throw new Error(data.error || 'You do not have permission to mark this ticket as seen.');
                    });
                }
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Success data:', data);
                if (data.success) {
                    // رفرش صفحه
                    location.reload();
                } else {
                    alert('Error: ' + (data.message || data.error || 'Unknown error'));
                    button.disabled = false;
                    button.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || 'An error occurred. Please try again.');
                button.disabled = false;
                button.innerHTML = originalText;
            });
        });
    });
});