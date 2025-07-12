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
    },
    {
        title: "Ozymandias",
        author: "Percy Bysshe Shelley",
        lines: [
            "I met a traveller from an antique land,",
            "Who said: Two vast and trunkless legs of stone",
            "Stand in the desert. Near them, on the sand,",
            "Half sunk, a shattered visage lies, whose frown,",
            "And wrinkled lip, and sneer of cold command,",
            "Tell that its sculptor well those passions read",
            "Which yet survive, stamped on these lifeless things,",
            "The hand that mocked them and the heart that fed:",
            "",
            "And on the pedestal these words appear:",
            "'My name is Ozymandias, king of kings:",
            "Look on my works, ye Mighty, and despair!'",
            "Nothing beside remains. Round the decay",
            "Of that colossal wreck, boundless and bare",
            "The lone and level sands stretch far away."
        ]
    },
    {
        title: "The Raven",
        author: "Edgar Allan Poe",
        lines: [
            "Once upon a midnight dreary, while I pondered, weak and weary,",
            "Over many a quaint and curious volume of forgotten lore—",
            "While I nodded, nearly napping, suddenly there came a tapping,",
            "As of some one gently rapping, rapping at my chamber door.",
            "'Tis some visitor,' I muttered, 'tapping at my chamber door—",
            "Only this and nothing more.'",
            "",
            "Ah, distinctly I remember it was in the bleak December;",
            "And each separate dying ember wrought its ghost upon the floor.",
            "Eagerly I wished the morrow;—vainly I had sought to borrow",
            "From my books surcease of sorrow—sorrow for the lost Lenore—",
            "For the rare and radiant maiden whom the angels name Lenore—",
            "Nameless here for evermore."
        ]
    },
    {
        title: "Sonnet 18",
        author: "William Shakespeare",
        lines: [
            "Shall I compare thee to a summer's day?",
            "Thou art more lovely and more temperate:",
            "Rough winds do shake the darling buds of May,",
            "And summer's lease hath all too short a date;",
            "",
            "Sometime too hot the eye of heaven shines,",
            "And often is his gold complexion dimm'd;",
            "And every fair from fair sometime declines,",
            "By chance or nature's changing course untrimm'd;",
            "",
            "But thy eternal summer shall not fade,",
            "Nor lose possession of that fair thou ow'st;",
            "Nor shall death brag thou wander'st in his shade,",
            "When in eternal lines to time thou grow'st:",
            "",
            "So long as men can breathe or eyes can see,",
            "So long lives this, and this gives life to thee."
        ]
    },
    {
        title: "Do Not Go Gentle Into That Good Night",
        author: "Dylan Thomas",
        lines: [
            "Do not go gentle into that good night,",
            "Old age should burn and rave at close of day;",
            "Rage, rage against the dying of the light.",
            "",
            "Though wise men at their end know dark is right,",
            "Because their words had forked no lightning they",
            "Do not go gentle into that good night.",
            "",
            "Good men, the last wave by, crying how bright",
            "Their frail deeds might have danced in a green bay,",
            "Rage, rage against the dying of the light.",
            "",
            "Wild men who caught and sang the sun in flight,",
            "And learn, too late, they grieved it on its way,",
            "Do not go gentle into that good night.",
            "",
            "Grave men, near death, who see with blinding sight",
            "Blind eyes could blaze like meteors and be gay,",
            "Rage, rage against the dying of the light."
        ]
    },
    {
        title: "If",
        author: "Rudyard Kipling",
        lines: [
            "If you can keep your head when all about you",
            "Are losing theirs and blaming it on you,",
            "If you can trust yourself when all men doubt you,",
            "But make allowance for their doubting too;",
            "",
            "If you can wait and not be tired by waiting,",
            "Or being lied about, don't deal in lies,",
            "Or being hated, don't give way to hating,",
            "And yet don't look too good, nor talk too wise:",
            "",
            "If you can dream—and not make dreams your master;",
            "If you can think—and not make thoughts your aim;",
            "If you can meet with Triumph and Disaster",
            "And treat those two impostors just the same;",
            "",
            "If you can bear to hear the truth you've spoken",
            "Twisted by knaves to make a trap for fools,",
            "Or watch the things you gave your life to, broken,",
            "And stoop and build 'em up with worn-out tools:"
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
    poemContainer.style.animation = `scroll ${scrollSpeed}s linear infinite`;
    poemContainer.style.animationPlayState = isPlaying ? 'running' : 'paused';
    
    // Ensure the poem starts from the bottom
    poemContainer.style.transform = 'translateY(100%)';
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
    
    poem.style.animation = `scroll ${scrollSpeed}s linear infinite`;
    speedBtn.textContent = `Speed: ${scrollSpeed}s`;
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const themeBtn = document.querySelector('.control-btn.theme');
    themeBtn.textContent = document.body.classList.contains('dark-theme') ? '☀️' : '🌙';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set up initial poem display
    updatePoemDisplay();
    updatePoemSelect();
    
    // Add event listeners
    document.querySelector('.control-btn.play').addEventListener('click', togglePlay);
    document.querySelector('.control-btn.speed').addEventListener('click', changeSpeed);
    document.querySelector('.control-btn.theme').addEventListener('click', toggleTheme);
    document.querySelector('.control-select').addEventListener('change', (e) => {
        currentPoemIndex = parseInt(e.target.value);
        updatePoemDisplay();
    });
}); 