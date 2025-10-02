document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    let selectedTicketId = null;
    let selectedRow = null;
    let highlightTimeout = null;

    // Click on delete button
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            selectedTicketId = this.getAttribute('data-ticket-id');
            const ticketTitle = this.getAttribute('data-ticket-title');
            const ticketNumber = this.getAttribute('data-ticket-number');

            // Find the related row
            selectedRow = this.closest('tr');

            // Highlight the row
            document.querySelectorAll('tr').forEach(row => {
                row.classList.remove('table-warning', 'selected-for-delete', 'selected-for-delete-delayed');
            });
            selectedRow.classList.add('table-warning', 'selected-for-delete');

            // Add row number as data attribute for display
            const rowIndex = Array.from(selectedRow.parentNode.children).indexOf(selectedRow) + 1;
            selectedRow.setAttribute('data-row-number', rowIndex);

            // Set Modal text with ticket number
            document.getElementById('deleteModalLabel').textContent = `Delete Ticket Number ${ticketNumber}`;
            document.getElementById('ticketNumberSpan').textContent = ticketNumber;
            document.getElementById('ticketNumberSpanStep2').textContent = ticketNumber;

            // Reset Modal to first step
            document.getElementById('step1').style.display = 'block';
            document.getElementById('step2').style.display = 'none';
            document.getElementById('confirmStep1').style.display = 'inline-block';
            document.getElementById('confirmStep2').style.display = 'none';
            document.getElementById('cancelBtn').textContent = 'No';

            deleteModal.show();
        });
    });

    // First confirmation step
    document.getElementById('confirmStep1').addEventListener('click', function () {
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'block';
        document.getElementById('confirmStep1').style.display = 'none';
        document.getElementById('confirmStep2').style.display = 'inline-block';
        document.getElementById('cancelBtn').textContent = 'Cancel';
    });

    // Final confirmation step
    document.getElementById('confirmStep2').addEventListener('click', function () {
        if (selectedTicketId) {
            window.location.href = `{% url 'tickets-destroy' 0 %}`.replace('0', selectedTicketId);
        }
    });

    // When Modal closes
    document.getElementById('deleteModal').addEventListener('hidden.bs.modal', function () {
        // Clear previous timeout if exists
        if (highlightTimeout) {
            clearTimeout(highlightTimeout);
        }

        // Keep highlight for 1 seconds (increased from 3 to 5 seconds)
        if (selectedRow) {
            selectedRow.classList.remove('selected-for-delete');
            selectedRow.classList.add('selected-for-delete-delayed');

            // Display row number in console for debug
            const rowNumber = selectedRow.getAttribute('data-row-number');
            console.log(`Row number ${rowNumber} was selected for deletion`);

            highlightTimeout = setTimeout(() => {
                selectedRow.classList.remove('selected-for-delete-delayed', 'table-warning');
                selectedRow.removeAttribute('data-row-number');
            }, 1000); // 1 seconds
        }

        selectedTicketId = null;
    });
});
