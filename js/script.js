document.addEventListener('DOMContentLoaded', () => {
    const poem = document.querySelector('.poem');
    const pauseBtn = document.getElementById('pauseBtn');
    const themeBtn = document.querySelector('.control-btn.theme');
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
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            themeBtn.textContent = document.body.classList.contains('dark-theme') ? '☀️' : '🌙';
        });
    }
}); 