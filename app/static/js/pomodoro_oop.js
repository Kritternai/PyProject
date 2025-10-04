/**
 * Pomodoro OOP Integration
 * Frontend integration for Pomodoro OOP API
 */

class PomodoroOOP {
    constructor() {
        this.baseUrl = '/api/pomodoro';
        this.activeSession = null;
        this.timer = null;
        this.isRunning = false;
    }

    // Session Management
    async startSession(sessionType = 'focus', duration = 25, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_type: sessionType,
                    duration: duration,
                    lesson_id: options.lessonId,
                    section_id: options.sectionId,
                    task_id: options.taskId,
                    mood_before: options.moodBefore,
                    notes: options.notes
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.activeSession = data.session;
                this.startTimer();
                console.log('✅ Session started:', data.session);
                return data.session;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error starting session:', error);
            throw error;
        }
    }

    async pauseSession() {
        if (!this.activeSession) {
            throw new Error('No active session');
        }

        try {
            const response = await fetch(`${this.baseUrl}/pause`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.activeSession.id
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.activeSession = data.session;
                this.stopTimer();
                console.log('✅ Session paused');
                return data.session;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error pausing session:', error);
            throw error;
        }
    }

    async resumeSession() {
        if (!this.activeSession) {
            throw new Error('No active session');
        }

        try {
            const response = await fetch(`${this.baseUrl}/resume`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.activeSession.id
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.activeSession = data.session;
                this.startTimer();
                console.log('✅ Session resumed');
                return data.session;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error resuming session:', error);
            throw error;
        }
    }

    async completeSession(feedback = {}) {
        if (!this.activeSession) {
            throw new Error('No active session');
        }

        try {
            const response = await fetch(`${this.baseUrl}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.activeSession.id,
                    productivity_score: feedback.productivityScore,
                    mood_after: feedback.moodAfter,
                    focus_score: feedback.focusScore,
                    energy_level: feedback.energyLevel,
                    difficulty_level: feedback.difficultyLevel,
                    notes: feedback.notes
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.activeSession = null;
                this.stopTimer();
                console.log('✅ Session completed');
                return data.session;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error completing session:', error);
            throw error;
        }
    }

    async interruptSession(reason = null) {
        if (!this.activeSession) {
            throw new Error('No active session');
        }

        try {
            const response = await fetch(`${this.baseUrl}/interrupt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.activeSession.id,
                    reason: reason
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.activeSession = data.session;
                this.stopTimer();
                console.log('✅ Session interrupted');
                return data.session;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error interrupting session:', error);
            throw error;
        }
    }

    async cancelSession() {
        if (!this.activeSession) {
            throw new Error('No active session');
        }

        try {
            const response = await fetch(`${this.baseUrl}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.activeSession.id
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.activeSession = null;
                this.stopTimer();
                console.log('✅ Session cancelled');
                return data.session;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error cancelling session:', error);
            throw error;
        }
    }

    // Session Queries
    async getActiveSession() {
        try {
            const response = await fetch(`${this.baseUrl}/active`);
            const data = await response.json();
            
            if (data.success) {
                this.activeSession = data.session;
                return data.session;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error getting active session:', error);
            throw error;
        }
    }

    async getUserSessions(limit = 50) {
        try {
            const response = await fetch(`${this.baseUrl}/sessions?limit=${limit}`);
            const data = await response.json();
            
            if (data.success) {
                return data.sessions;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error getting user sessions:', error);
            throw error;
        }
    }

    async getLessonSessions(lessonId) {
        try {
            const response = await fetch(`${this.baseUrl}/lessons/${lessonId}/sessions`);
            const data = await response.json();
            
            if (data.success) {
                return data.sessions;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error getting lesson sessions:', error);
            throw error;
        }
    }

    // Statistics
    async getStatistics(period = 'month') {
        try {
            const response = await fetch(`${this.baseUrl}/statistics?period=${period}`);
            const data = await response.json();
            
            if (data.success) {
                return data.statistics;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error getting statistics:', error);
            throw error;
        }
    }

    async getProductivityInsights(days = 30) {
        try {
            const response = await fetch(`${this.baseUrl}/insights?days=${days}`);
            const data = await response.json();
            
            if (data.success) {
                return data.insights;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('❌ Error getting insights:', error);
            throw error;
        }
    }

    // Timer Management
    startTimer() {
        if (this.timer) {
            clearInterval(this.timer);
        }
        
        this.isRunning = true;
        this.timer = setInterval(() => {
            this.updateTimer();
        }, 1000);
    }

    stopTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        this.isRunning = false;
    }

    updateTimer() {
        if (this.activeSession && this.activeSession.time_remaining > 0) {
            // Update UI here
            this.onTimerUpdate(this.activeSession.time_remaining);
        } else if (this.activeSession && this.activeSession.time_remaining <= 0) {
            // Session completed
            this.onSessionComplete();
        }
    }

    // Event Handlers (Override these)
    onTimerUpdate(timeRemaining) {
        console.log(`⏰ Time remaining: ${timeRemaining} minutes`);
    }

    onSessionComplete() {
        console.log('🎉 Session completed!');
        this.stopTimer();
    }

    // Utility Methods
    formatTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }

    getSessionTypeName(sessionType) {
        const names = {
            'focus': 'Focus Time',
            'short_break': 'Short Break',
            'long_break': 'Long Break'
        };
        return names[sessionType] || sessionType;
    }

    getStatusName(status) {
        const names = {
            'active': 'Active',
            'paused': 'Paused',
            'completed': 'Completed',
            'interrupted': 'Interrupted',
            'cancelled': 'Cancelled'
        };
        return names[status] || status;
    }
}

// Global instance
window.PomodoroOOP = new PomodoroOOP();

// Example usage
window.PomodoroOOP.onTimerUpdate = function(timeRemaining) {
    // Update UI elements
    const timerDisplay = document.getElementById('timer-display');
    if (timerDisplay) {
        timerDisplay.textContent = this.formatTime(timeRemaining);
    }
};

window.PomodoroOOP.onSessionComplete = function() {
    // Show completion notification
    alert('Session completed! Great job! 🎉');
    
    // Auto-start next session if enabled
    if (this.activeSession && this.activeSession.auto_start_next) {
        this.startNextSession();
    }
};

console.log('🍅 Pomodoro OOP Integration loaded!');
