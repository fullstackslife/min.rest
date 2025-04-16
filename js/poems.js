const poems = [
    {
        title: "The Road Not Taken",
        author: "Robert Frost",
        lines: [
            "Two roads diverged in a yellow wood,",
            "And sorry I could not travel both",
            "And be one traveler, long I stood",
            "And looked down one as far as I could",
            "To where it bent in the undergrowth;",
            "",
            "Then took the other, as just as fair,",
            "And having perhaps the better claim,",
            "Because it was grassy and wanted wear;",
            "Though as for that the passing there",
            "Had worn them really about the same,",
            "",
            "And both that morning equally lay",
            "In leaves no step had trodden black.",
            "Oh, I kept the first for another day!",
            "Yet knowing how way leads on to way,",
            "I doubted if I should ever come back.",
            "",
            "I shall be telling this with a sigh",
            "Somewhere ages and ages hence:",
            "Two roads diverged in a wood, and I—",
            "I took the one less traveled by,",
            "And that has made all the difference."
        ]
    },
    {
        title: "Stopping by Woods on a Snowy Evening",
        author: "Robert Frost",
        lines: [
            "Whose woods these are I think I know.",
            "His house is in the village though;",
            "He will not see me stopping here",
            "To watch his woods fill up with snow.",
            "",
            "My little horse must think it queer",
            "To stop without a farmhouse near",
            "Between the woods and frozen lake",
            "The darkest evening of the year.",
            "",
            "He gives his harness bells a shake",
            "To ask if there is some mistake.",
            "The only other sound's the sweep",
            "Of easy wind and downy flake.",
            "",
            "The woods are lovely, dark and deep,",
            "But I have promises to keep,",
            "And miles to go before I sleep,",
            "And miles to go before I sleep."
        ]
    },
    {
        title: "Whisperscroll",
        author: "Anonymous",
        lines: [
            "In quiet hours the world exhales,",
            "Soft winds drift where silence sails.",
            "The stars blink slow in velvet skies,",
            "And dreams take shape behind closed eyes.",
            "",
            "Each breath a tide, both in and out,",
            "A moment's peace, devoid of doubt.",
            "Let stillness be your gentle guide,",
            "And find the calm you hold inside."
        ]
    }
];

let currentPoemIndex = 0;
let isPlaying = true;
let scrollSpeed = 60; // seconds to scroll through entire poem

function updatePoemDisplay() {
    const poem = poems[currentPoemIndex];
    document.querySelector('.poem-title').textContent = poem.title;
    document.querySelector('.poem-author').textContent = poem.author;
    
    const poemContainer = document.querySelector('.poem');
    poemContainer.innerHTML = '';
    
    poem.lines.forEach(line => {
        const p = document.createElement('p');
        p.textContent = line;
        poemContainer.appendChild(p);
    });

    // Reset animation
    poemContainer.style.animation = 'none';
    poemContainer.offsetHeight; // Trigger reflow
    poemContainer.style.animation = `scroll ${scrollSpeed}s linear`;
    poemContainer.style.animationPlayState = isPlaying ? 'running' : 'paused';
}

function updatePoemSelect() {
    const select = document.querySelector('.control-select');
    select.innerHTML = '';
    
    poems.forEach((poem, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${poem.title} - ${poem.author}`;
        if (index === currentPoemIndex) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

function togglePlay() {
    const poem = document.querySelector('.poem');
    const playBtn = document.querySelector('.control-btn.play');
    
    isPlaying = !isPlaying;
    poem.style.animationPlayState = isPlaying ? 'running' : 'paused';
    playBtn.textContent = isPlaying ? '⏸' : '▶';
}

function changeSpeed() {
    scrollSpeed = scrollSpeed === 60 ? 120 : 60;
    const poem = document.querySelector('.poem');
    const speedBtn = document.querySelector('.control-btn.speed');
    
    poem.style.animationDuration = `${scrollSpeed}s`;
    speedBtn.textContent = `Speed: ${scrollSpeed}s`;
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const themeBtn = document.querySelector('.control-btn.theme');
    themeBtn.textContent = document.body.classList.contains('dark-theme') ? '☀️' : '🌙';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updatePoemDisplay();
    updatePoemSelect();
    
    // Event listeners
    document.querySelector('.control-select').addEventListener('change', (e) => {
        currentPoemIndex = parseInt(e.target.value);
        updatePoemDisplay();
    });
    
    document.querySelector('.control-btn.play').addEventListener('click', togglePlay);
    document.querySelector('.control-btn.speed').addEventListener('click', changeSpeed);
    document.querySelector('.control-btn.theme').addEventListener('click', toggleTheme);
}); 