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
            document.body.style.setProperty('--bg-color', '#1b2735');
            document.body.style.setProperty('--fade-color', '#111');
            themeBtn.textContent = '🌙';
        } else {
            document.body.style.setProperty('--bg-color', '#f0f0f0');
            document.body.style.setProperty('--fade-color', '#fff');
            themeBtn.textContent = '☀️';
        }
    });
}); 