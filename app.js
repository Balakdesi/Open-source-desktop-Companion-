// DOM Element Selectors
const timerDisplay = document.getElementById('timer-display');
const timerStatus = document.getElementById('timer-status');
const btnStart = document.getElementById('btn-start');
const btnPause = document.getElementById('btn-pause');
const btnReset = document.getElementById('btn-reset');
const catCharacter = document.getElementById('cat-character');
const interactiveZone = document.getElementById('interactive-zone');
const pupils = document.querySelectorAll('.pupil');

// Application Configuration Parameters
let timeLeft = 1500; // 25 minutes standard configuration
let timerId = null;
let isWorking = true;

// 1. Pomodoro Logic System
function updateTimerInterface() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function startTimer() {
    if (timerId !== null) return;
    
    // Switch character presentation to focus state
    catCharacter.classList.add('sleeping');
    timerStatus.textContent = isWorking ? "Deep Focus Period..." : "Rest Cycle...";
    
    timerId = setInterval(() => {
        if (timeLeft > 0) {
            timeLeft--;
            updateTimerInterface();
        } else {
            handleCycleCompletion();
        }
    }, 1000);
}

function pauseTimer() {
    clearInterval(timerId);
    timerId = null;
    catCharacter.classList.remove('sleeping');
    timerStatus.textContent = "Paused";
}

function resetTimer() {
    pauseTimer();
    isWorking = true;
    timeLeft = 1500;
    timerStatus.textContent = "Focus Time";
    updateTimerInterface();
}

function handleCycleCompletion() {
    pauseTimer();
    isWorking = !isWorking;
    timeLeft = isWorking ? 1500 : 300; // 25m work or 5m break
    timerStatus.textContent = isWorking ? "Ready to Work?" : "Time for a Break!";
    updateTimerInterface();
}

// 2. Trigonometric Interactive Eye-Tracking System
function handlePointerTracking(clientX, clientY) {
    // If the companion is asleep, bypass tracking calculation
    if (catCharacter.classList.contains('sleeping')) return;

    pupils.forEach(pupil => {
        const eye = pupil.parentElement;
        const rect = eye.getBoundingClientRect();
        
        // Locate the geometric center point coordinates of the eye socket
        const eyeCenterX = rect.left + rect.width / 2;
        const eyeCenterY = rect.top + rect.height / 2;
        
        // Compute delta tracking vectors
        const deltaX = clientX - eyeCenterX;
        const deltaY = clientY - eyeCenterY;
        
        // Determine vector heading using atan2
        const angle = Math.atan2(deltaY, deltaX);
        
        // Restrict maximum linear pupillary travel boundary offset displacement
        const maxDistance = 4; 
        const targetX = Math.cos(angle) * maxDistance;
        const targetY = Math.sin(angle) * maxDistance;
        
        pupil.style.transform = `translate(${targetX}px, ${targetY}px)`;
    });
}

// Event Listeners for both Desktop Environments and Mobile Displays
window.addEventListener('mousemove', (e) => {
    handlePointerTracking(e.clientX, e.clientY);
});

window.addEventListener('touchmove', (e) => {
    if (e.touches.length > 0) {
        handlePointerTracking(e.touches[0].clientX, e.touches[0].clientY);
    }
});

btnStart.addEventListener('click', startTimer);
btnPause.addEventListener('click', pauseTimer);
btnReset.addEventListener('click', resetTimer);

// Initialize Display Interface State
updateTimerInterface();