let rowSortOrder = 'asc';

function toggleSort(column) {
    if (column === 'row') {

        const icon = document.getElementById('row-sort-icon');

        if (rowSortOrder === 'asc') {
            icon.classList.remove('bi-sort-down');
            icon.classList.add('bi-sort-up');
            rowSortOrder = 'desc';
        } else {
            icon.classList.remove('bi-sort-up');
            icon.classList.add('bi-sort-down');
            rowSortOrder = 'asc';
        }
        sortTable(column, rowSortOrder);
    }
}

function sortTable(column, order) {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        let aValue, bValue;

        if (column === 'row') {
            aValue = parseInt(a.cells[0].textContent);
            bValue = parseInt(b.cells[0].textContent);
        }
        if (order === 'asc') {
            return aValue - bValue;
        } else {
            return bValue - aValue;
        }
    });

    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    rows.forEach(row => {
        tbody.appendChild(row);
    });
}
