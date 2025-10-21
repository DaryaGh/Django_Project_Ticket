document.addEventListener("DOMContentLoaded", function () {
    const toastElList = document.querySelectorAll('.toast');
    toastElList.forEach((toastEl, index) => {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 2000
        });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', function () {
            this.remove();
        });
    });
});