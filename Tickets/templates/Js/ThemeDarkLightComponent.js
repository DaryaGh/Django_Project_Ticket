document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;

    function applyTheme(theme) {
        localStorage.setItem('theme', theme);

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

            document.querySelectorAll('.card').forEach(card => {
                card.style.backgroundColor = '#2b3035';
                card.style.color = '#dee2e6';
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

            document.querySelectorAll('.card').forEach(card => {
                card.style.backgroundColor = '';
                card.style.color = '';
            });

            themeToggle.innerHTML = '<i class="bi bi-moon-fill fs-5 text-warning"></i>';
        }
    }

    function toggleTheme() {
        const currentTheme = localStorage.getItem('theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    }

    function initializeTheme() {
        const savedTheme = localStorage.getItem('theme');

        if (savedTheme) {
            applyTheme(savedTheme);
        } else {
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = systemDark ? 'dark' : 'light';
            applyTheme(initialTheme);
        }
    }

    initializeTheme();

    themeToggle.addEventListener('click', toggleTheme);

    window.addEventListener('load', function() {
        setTimeout(initializeTheme, 100);
    });
});