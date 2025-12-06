document.querySelector('input[name="attachments"]').addEventListener('change', function (e) {
    const previewContainer = document.getElementById('file-preview-container');
    const preview = document.getElementById('file-preview');

    // پاک کردن فقط preview فایل‌های جدید
    preview.innerHTML = '';
    // مخفی کردن container اگر هیچ فایل جدیدی انتخاب نشده
    if (e.target.files.length === 0) {
        previewContainer.style.display = 'none';
        return;
    }
    // نمایش container برای فایل‌های جدید
    previewContainer.style.display = 'block';
    // اضافه کردن هدر جدید برای مشخص کردن فایل‌های جدید
    const header = previewContainer.querySelector('h5');
    if (header) {
        header.textContent = 'New Files Preview (Selected Now):';
    }
    // ایجاد preview برای هر فایل جدید
    Array.from(e.target.files).forEach(file => {
        const col = document.createElement('div');
        col.className = 'col';
        col.setAttribute('data-file-name', file.name);
        // نشانگر فایل جدید
        col.innerHTML = `
            <div class="position-relative">
                <span class="position-absolute top-0 start-0 badge bg-success" style="z-index: 10;">
                    New
                </span>
        `;
        const reader = new FileReader();
        reader.onload = function (e) {
            let previewHtml = '';

            if (file.type.startsWith('image/')) {
                previewHtml = `
                    <div class="text-center">
                        <img src="${e.target.result}" class="img-fluid rounded shadow-sm" style="max-height: 150px; object-fit: cover;">
                        <p class="mt-2 small text-muted text-truncate" style="max-width: 150px;">${file.name}</p>
                    </div>`;
            } else if (file.type === 'application/pdf') {
                previewHtml = `
                    <div class="text-center">
                        <i class="bi bi-file-earmark-pdf-fill text-danger fs-1"></i>
                        <p class="mt-2 small text-muted text-truncate" style="max-width: 150px;">${file.name}</p>
                        <small class="text-secondary">PDF • ${(file.size / 1024 / 1024).toFixed(2)} MB</small>
                    </div>`;
            } else {
                const icon = file.type.includes('word') ? 'file-earmark-word' :
                    file.type.includes('excel') ? 'file-earmark-excel' :
                        file.type.includes('zip') ? 'file-earmark-zip' : 'file-earmark-text';
                previewHtml = `
                    <div class="text-center">
                        <i class="bi bi-${icon}-fill fs-1 text-secondary"></i>
                        <p class="mt-2 small text-muted text-truncate" style="max-width: 150px;">${file.name}</p>
                        <small class="text-secondary">${file.type.split('/')[1].toUpperCase()}</small>
                    </div>`;
            }
            col.innerHTML += previewHtml + '</div>';
        };
        reader.readAsDataURL(file);
        preview.appendChild(col);
    });
});