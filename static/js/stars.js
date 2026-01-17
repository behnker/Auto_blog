
document.addEventListener('DOMContentLoaded', () => {
    const starContainer = document.getElementById('star-field');
    if (!starContainer) return;

    const starCount = 50;

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('absolute', 'rounded-full', 'bg-white', 'animate-twinkle');

        // Random Properties
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        const size = Math.random() * 2 + 1;
        const opacity = Math.random() * 0.5 + 0.1;
        const duration = Math.random() * 3 + 2;

        star.style.left = `${x}%`;
        star.style.top = `${y}%`;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.opacity = opacity;
        star.style.animationDuration = `${duration}s`;

        starContainer.appendChild(star);
    }
});
