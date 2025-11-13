/*
 * Lógica para el Modo Oscuro (Dark Mode)
 * Se aplica en base.html (login, register, profile)
 */

document.addEventListener('DOMContentLoaded', () => {
    
    const themeToggleButton = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    // Función para aplicar el tema (dark/light)
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            if (themeIcon) themeIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            if (themeIcon) themeIcon.classList.replace('bi-sun-fill', 'bi-moon-fill');
        }
    };

    // Obtener preferencia guardada
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Aplicar tema al cargar
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        applyTheme(systemPrefersDark ? 'dark' : 'light');
    }

    // Listener para el botón
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = (currentTheme === 'dark') ? 'light' : 'dark';
            
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }
});