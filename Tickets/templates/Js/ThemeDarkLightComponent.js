document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    function getInitialTheme() {
        const saved = localStorage.getItem('theme');
        if (saved) return saved;
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        return systemDark ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        document.body.setAttribute('data-bs-theme', theme);

        if (theme === 'dark') {
            document.body.style.backgroundColor = '#212529';
            document.body.style.color = '#dee2e6';

            document.querySelectorAll('input, select, textarea').forEach(el => {
                el.style.backgroundColor = '#2b3035';
                el.style.color = '#dee2e6';
                el.style.borderColor = '#495057';
            });
            themeToggle.innerHTML = '<i class="bi bi-sun-fill fs-5 text-warning"></i>';

        } else {
            document.body.style.backgroundColor = '#ffffff';
            document.body.style.color = '#212529';

            document.querySelectorAll('input, select, textarea').forEach(el => {
                el.style.backgroundColor = '';
                el.style.color = '';
                el.style.borderColor = '';
            });
            themeToggle.innerHTML = '<i class="bi bi-moon-fill fs-5 text-warning"></i>';
        }
    }

    function toggleTheme() {
        const current = htmlElement.getAttribute('data-bs-theme') || 'light';
        const newTheme = current === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    }

    const initialTheme = getInitialTheme();
    applyTheme(initialTheme);
    themeToggle.addEventListener('click', toggleTheme);
});