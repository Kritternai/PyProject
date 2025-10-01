/**
 * Pomodoro Timer - Hard Code Version
 * Simple timer with focus/break sessions
 */

// Hard coded values
const FOCUS_TIME = 25 * 60;        // 25 minutes in seconds
const SHORT_BREAK = 5 * 60;        // 5 minutes in seconds
const LONG_BREAK = 15 * 60;        // 15 minutes in seconds
const LONG_BREAK_INTERVAL = 4;     // Every 4 pomodoros

// State management
let currentTime = FOCUS_TIME;
let currentSession = 'focus';
let completedPomodoros = 0;
let isRunning = false;
let timer = null;

// DOM elements
let timerDisplay = null;
let sessionTypeDisplay = null;
let counterDisplay = null;
let startBtn = null;
let pauseBtn = null;
let resetBtn = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePomodoro();
});

function initializePomodoro() {
    // Get DOM elements
    timerDisplay = document.getElementById('timer-display');
    sessionTypeDisplay = document.getElementById('session-type');
    counterDisplay = document.getElementById('pomodoro-counter');
    startBtn = document.getElementById('start-btn');
    pauseBtn = document.getElementById('pause-btn');
    resetBtn = document.getElementById('reset-btn');
    
    // Set up event listeners
    if (startBtn) startBtn.addEventListener('click', startTimer);
    if (pauseBtn) pauseBtn.addEventListener('click', pauseTimer);
    if (resetBtn) resetBtn.addEventListener('click', resetTimer);
    
    // Update display
    updateDisplay();
    
    console.log('Pomodoro Timer initialized');
}

function startTimer() {
    if (!isRunning) {
        isRunning = true;
        timer = setInterval(tick, 1000);
        updateButtons();
        console.log('Timer started');
    }
}

function pauseTimer() {
    if (isRunning) {
        isRunning = false;
        clearInterval(timer);
        updateButtons();
        console.log('Timer paused');
    }
}

function resetTimer() {
    isRunning = false;
    clearInterval(timer);
    currentTime = getSessionDuration(currentSession);
    updateDisplay();
    updateButtons();
    console.log('Timer reset');
}

function tick() {
    currentTime--;
    updateDisplay();
    
    if (currentTime <= 0) {
        completeSession();
    }
}

function completeSession() {
    isRunning = false;
    clearInterval(timer);
    
    // Show notification
    showNotification();
    
    // Update counter
    if (currentSession === 'focus') {
        completedPomodoros++;
    }
    
    // Move to next session
    nextSession();
    
    console.log('Session completed:', currentSession);
}

function nextSession() {
    if (currentSession === 'focus') {
        if (completedPomodoros % LONG_BREAK_INTERVAL === 0) {
            currentSession = 'long_break';
        } else {
            currentSession = 'short_break';
        }
    } else {
        currentSession = 'focus';
    }
    
    currentTime = getSessionDuration(currentSession);
    updateDisplay();
    updateButtons();
}

function getSessionDuration(sessionType) {
    switch (sessionType) {
        case 'focus': return FOCUS_TIME;
        case 'short_break': return SHORT_BREAK;
        case 'long_break': return LONG_BREAK;
        default: return FOCUS_TIME;
    }
}

function updateDisplay() {
    if (timerDisplay) {
        const minutes = Math.floor(currentTime / 60);
        const seconds = currentTime % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    if (sessionTypeDisplay) {
        const sessionNames = {
            'focus': 'Focus Time',
            'short_break': 'Short Break',
            'long_break': 'Long Break'
        };
        sessionTypeDisplay.textContent = sessionNames[currentSession] || 'Focus Time';
    }
    
    if (counterDisplay) {
        counterDisplay.textContent = `${completedPomodoros}/${LONG_BREAK_INTERVAL}`;
    }
}

function updateButtons() {
    if (startBtn && pauseBtn) {
        if (isRunning) {
            startBtn.style.display = 'none';
            pauseBtn.style.display = 'inline-block';
        } else {
            startBtn.style.display = 'inline-block';
            pauseBtn.style.display = 'none';
        }
    }
}

function showNotification() {
    if (Notification.permission === 'granted') {
        const sessionNames = {
            'focus': 'Focus Time Complete!',
            'short_break': 'Break Time Complete!',
            'long_break': 'Long Break Complete!'
        };
        
        new Notification(sessionNames[currentSession] || 'Session Complete!', {
            body: 'Time for the next session!',
            icon: '/static/icons/pomodoro.png'
        });
    }
}

// Request notification permission
if (Notification.permission === 'default') {
    Notification.requestPermission();
}

// Export for global access
window.PomodoroTimer = {
    start: startTimer,
    pause: pauseTimer,
    reset: resetTimer,
    getState: () => ({
        currentTime,
        currentSession,
        completedPomodoros,
        isRunning
    })
};
