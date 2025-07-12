document.addEventListener('DOMContentLoaded', () => {
    const poem = document.querySelector('.poem');
    const pauseBtn = document.getElementById('pauseBtn');
    const themeBtn = document.getElementById('themeBtn');
    let isPaused = false;
    let isDarkTheme = true;

    // Pause/Resume functionality
    pauseBtn.addEventListener('click', () => {
        isPaused = !isPaused;
        if (isPaused) {
            poem.style.animationPlayState = 'paused';
            pauseBtn.textContent = '▶';
        } else {
            poem.style.animationPlayState = 'running';
            pauseBtn.textContent = '⏸';
        }
    });

    // Theme toggle functionality
    themeBtn.addEventListener('click', () => {
        isDarkTheme = !isDarkTheme;
        if (isDarkTheme) {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
            themeBtn.textContent = '🌙';
        } else {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
            themeBtn.textContent = '☀️';
        }
    });

    // Set initial theme
    document.body.classList.add('dark-theme');
}); 