/**
 * Simple Pomodoro Timer
 * Standalone JavaScript implementation
 */

class SimplePomodoro {
    constructor() {
        this.isRunning = false;
        this.isPaused = false;
        this.timeLeft = 25 * 60; // 25 minutes in seconds
        this.sessionType = 'focus'; // focus, short_break, long_break
        this.sessionCount = 0;
        this.timer = null;
        this.totalSessions = 0;
        
        this.initializeUI();
        this.bindEvents();
    }
    
    initializeUI() {
        console.log('🎨 Initializing UI...');
        this.timerDisplay = document.getElementById('timer-display');
        this.sessionTypeDisplay = document.getElementById('session-type');
        this.startBtn = document.getElementById('start-btn');
        this.pauseBtn = document.getElementById('pause-btn');
        this.resumeBtn = document.getElementById('resume-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.sessionCounter = document.getElementById('pomodoro-counter');
        
        console.log('🎯 UI Elements found:', {
            timerDisplay: !!this.timerDisplay,
            sessionTypeDisplay: !!this.sessionTypeDisplay,
            startBtn: !!this.startBtn,
            pauseBtn: !!this.pauseBtn,
            resumeBtn: !!this.resumeBtn,
            resetBtn: !!this.resetBtn,
            sessionCounter: !!this.sessionCounter
        });
        
        this.updateDisplay();
        
        // Re-bind events after UI is ready
        setTimeout(() => {
            this.bindEvents();
        }, 100);
    }
    
    bindEvents() {
        console.log('🔗 Binding Pomodoro events...');
        
        // Use event delegation for SPA compatibility
        const mainContent = document.getElementById('main-content');
        if (!mainContent) {
            console.log('❌ Main content not found, retrying in 200ms...');
            setTimeout(() => this.bindEvents(), 200);
            return;
        }
        
        // Remove existing listeners to prevent duplicates
        if (this.mainContentListener) {
            mainContent.removeEventListener('click', this.mainContentListener);
            console.log('🧹 Removed existing listener');
        }
        
        // Use event delegation instead of direct element binding
        this.mainContentListener = (e) => {
            if (e.target && e.target.id === 'start-btn') {
                console.log('🎯 Start button clicked via delegation!');
                this.start();
            } else if (e.target && e.target.id === 'pause-btn') {
                console.log('🎯 Pause button clicked via delegation!');
                this.pause();
            } else if (e.target && e.target.id === 'resume-btn') {
                console.log('🎯 Resume button clicked via delegation!');
                this.resume();
            } else if (e.target && e.target.id === 'reset-btn') {
                console.log('🎯 Reset button clicked via delegation!');
                this.reset();
            }
        };
        
        mainContent.addEventListener('click', this.mainContentListener);
        console.log('✅ Event delegation set up for SPA');
        
        // Also try to find elements for display updates
        this.startBtn = document.getElementById('start-btn');
        this.pauseBtn = document.getElementById('pause-btn');
        this.resumeBtn = document.getElementById('resume-btn');
        this.resetBtn = document.getElementById('reset-btn');
        
        console.log('Elements found:', {
            startBtn: !!this.startBtn,
            pauseBtn: !!this.pauseBtn,
            resumeBtn: !!this.resumeBtn,
            resetBtn: !!this.resetBtn
        });
    }
    
    start() {
        console.log('🚀 Starting Pomodoro session...');
        console.log('Current state:', {
            isRunning: this.isRunning,
            isPaused: this.isPaused,
            timeLeft: this.timeLeft
        });
        
        if (this.isRunning) {
            console.log('❌ Session already running, ignoring start');
            return;
        }
        
        this.isRunning = true;
        this.isPaused = false;
        this.updateButtons();
        
        console.log('⏰ Starting timer...');
        this.timer = setInterval(() => {
            this.timeLeft--;
            console.log('⏱️ Timer tick:', this.timeLeft, 'seconds left');
            this.updateDisplay();
            
            if (this.timeLeft <= 0) {
                console.log('🏁 Timer completed!');
                this.completeSession();
            }
        }, 1000);
        
        this.showMessage('Session started! 🍅', 'success');
        console.log('✅ Pomodoro session started successfully!');
    }
    
    pause() {
        if (!this.isRunning || this.isPaused) return;
        
        this.isPaused = true;
        clearInterval(this.timer);
        this.updateButtons();
        this.showMessage('Session paused', 'info');
    }
    
    resume() {
        if (!this.isRunning || !this.isPaused) return;
        
        this.isPaused = false;
        this.timer = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();
            
            if (this.timeLeft <= 0) {
                this.completeSession();
            }
        }, 1000);
        
        this.updateButtons();
        this.showMessage('Session resumed', 'success');
    }
    
    reset() {
        this.isRunning = false;
        this.isPaused = false;
        clearInterval(this.timer);
        
        // Reset to focus session
        this.sessionType = 'focus';
        this.timeLeft = 25 * 60;
        this.updateDisplay();
        this.updateButtons();
        
        this.showMessage('Session reset', 'info');
    }
    
    completeSession() {
        this.isRunning = false;
        this.isPaused = false;
        clearInterval(this.timer);
        
        this.sessionCount++;
        this.totalSessions++;
        
        // Play notification sound
        this.playNotification();
        
        // Show completion message
        this.showMessage('Session completed! Great job! 🎉', 'success');
        
        // Auto-start break or next session
        setTimeout(() => {
            this.startBreak();
        }, 2000);
        
        this.updateButtons();
    }
    
    startBreak() {
        if (this.sessionCount % 4 === 0) {
            // Long break every 4 sessions
            this.sessionType = 'long_break';
            this.timeLeft = 15 * 60; // 15 minutes
        } else {
            // Short break
            this.sessionType = 'short_break';
            this.timeLeft = 5 * 60; // 5 minutes
        }
        
        this.updateDisplay();
        this.showMessage(`Break time! ${this.sessionType === 'long_break' ? 'Long' : 'Short'} break started`, 'info');
        
        // Auto-start break timer
        this.start();
    }
    
    updateDisplay() {
        console.log('🔄 Updating display, timeLeft:', this.timeLeft);
        
        // Re-find timer display element in case it wasn't ready before
        if (!this.timerDisplay) {
            this.timerDisplay = document.getElementById('timer-display');
            console.log('🔍 Re-finding timer display:', !!this.timerDisplay);
        }
        
        if (this.timerDisplay) {
            const minutes = Math.floor(this.timeLeft / 60);
            const seconds = this.timeLeft % 60;
            const displayText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            this.timerDisplay.textContent = displayText;
            console.log('📺 Display updated to:', displayText);
        } else {
            console.log('❌ Timer display element not found');
        }
        
        // Re-find session type display element
        if (!this.sessionTypeDisplay) {
            this.sessionTypeDisplay = document.getElementById('session-type');
        }
        
        if (this.sessionTypeDisplay) {
            const typeNames = {
            'focus': 'Focus Time',
            'short_break': 'Short Break',
            'long_break': 'Long Break'
        };
            this.sessionTypeDisplay.textContent = typeNames[this.sessionType] || 'Focus Time';
        }
        
        // Re-find session counter element
        if (!this.sessionCounter) {
            this.sessionCounter = document.getElementById('pomodoro-counter');
        }
        
        if (this.sessionCounter) {
            this.sessionCounter.textContent = `${this.sessionCount}/4`;
        }
    }
    
    updateButtons() {
        // Re-find button elements in case they weren't ready before
        if (!this.startBtn) this.startBtn = document.getElementById('start-btn');
        if (!this.pauseBtn) this.pauseBtn = document.getElementById('pause-btn');
        if (!this.resumeBtn) this.resumeBtn = document.getElementById('resume-btn');
        if (!this.resetBtn) this.resetBtn = document.getElementById('reset-btn');
        
        if (this.startBtn) {
            this.startBtn.style.display = this.isRunning ? 'none' : 'inline-block';
        }
        if (this.pauseBtn) {
            this.pauseBtn.style.display = (this.isRunning && !this.isPaused) ? 'inline-block' : 'none';
        }
        if (this.resumeBtn) {
            this.resumeBtn.style.display = (this.isRunning && this.isPaused) ? 'inline-block' : 'none';
        }
        if (this.resetBtn) {
            this.resetBtn.style.display = this.isRunning ? 'inline-block' : 'none';
        }
    }
    
    playNotification() {
        // Create audio context for notification sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (e) {
            console.log('Audio notification not available');
        }
    }
    
    showMessage(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    // Public methods for external access
    getStatus() {
        return {
            isRunning: this.isRunning,
            isPaused: this.isPaused,
            timeLeft: this.timeLeft,
            sessionType: this.sessionType,
            sessionCount: this.sessionCount,
            totalSessions: this.totalSessions
        };
    }
    
    setSessionType(type) {
        this.sessionType = type;
        if (type === 'focus') {
            this.timeLeft = 25 * 60;
        } else if (type === 'short_break') {
            this.timeLeft = 5 * 60;
        } else if (type === 'long_break') {
            this.timeLeft = 15 * 60;
        }
        this.updateDisplay();
    }
}

// Initialize when DOM is loaded or when fragment is loaded
function initializePomodoro() {
    if (!window.pomodoro) {
        window.pomodoro = new SimplePomodoro();
        console.log('🍅 Simple Pomodoro Timer loaded!');
    } else {
        console.log('🍅 Pomodoro Timer already exists, re-binding events...');
        window.pomodoro.bindEvents();
    }
}

// Global event delegation for SPA compatibility (backup)
let globalPomodoroListener = function(e) {
    if (e.target && e.target.id === 'start-btn' && window.pomodoro) {
        console.log('🎯 Start button clicked via global delegation!');
        window.pomodoro.start();
    } else if (e.target && e.target.id === 'pause-btn' && window.pomodoro) {
        console.log('🎯 Pause button clicked via global delegation!');
        window.pomodoro.pause();
    } else if (e.target && e.target.id === 'resume-btn' && window.pomodoro) {
        console.log('🎯 Resume button clicked via global delegation!');
        window.pomodoro.resume();
    } else if (e.target && e.target.id === 'reset-btn' && window.pomodoro) {
        console.log('🎯 Reset button clicked via global delegation!');
        window.pomodoro.reset();
    }
};

// Only add global listener once
if (!window.pomodoroGlobalListenerAdded) {
    document.addEventListener('click', globalPomodoroListener);
    window.pomodoroGlobalListenerAdded = true;
    console.log('✅ Global Pomodoro listener added');
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initializePomodoro);

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePomodoro);
} else {
    initializePomodoro();
}
