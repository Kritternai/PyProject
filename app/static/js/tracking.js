/**
 * Progress Tracking - Hard Code Version
 * Simple tracking with charts and statistics
 */

// Hard coded goals
const DAILY_GOALS = {
    pomodoros: 8,
    studyTime: 240, // minutes
    lessons: 3,
    notes: 5
};

const WEEKLY_GOALS = {
    pomodoros: 40,
    studyTime: 1200, // minutes
    lessons: 15,
    notes: 25
};

// State management
let todayProgress = {
    pomodoros: 0,
    studyTime: 0,
    lessons: 0,
    notes: 0
};

let weeklyProgress = {
    pomodoros: [0, 0, 0, 0, 0, 0, 0],
    studyTime: [0, 0, 0, 0, 0, 0, 0],
    lessons: [0, 0, 0, 0, 0, 0, 0],
    notes: [0, 0, 0, 0, 0, 0, 0]
};

// Chart instances
let progressChart = null;
let timeChart = null;

// DOM elements
let progressBars = {};
let goalDisplays = {};
let chartContainers = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTracking();
});

function initializeTracking() {
    // Get DOM elements
    progressBars = {
        pomodoros: document.getElementById('pomodoro-progress'),
        studyTime: document.getElementById('study-time-progress'),
        lessons: document.getElementById('lessons-progress'),
        notes: document.getElementById('notes-progress')
    };
    
    goalDisplays = {
        pomodoros: document.getElementById('pomodoro-goal'),
        studyTime: document.getElementById('study-time-goal'),
        lessons: document.getElementById('lessons-goal'),
        notes: document.getElementById('notes-goal')
    };
    
    chartContainers = {
        progress: document.getElementById('progress-chart'),
        time: document.getElementById('time-chart')
    };
    
    // Load saved data
    loadProgress();
    
    // Initialize charts
    initializeCharts();
    
    // Update display
    updateDisplay();
    
    console.log('Progress Tracking initialized');
}

function updateProgress(type, amount) {
    if (todayProgress.hasOwnProperty(type)) {
        todayProgress[type] += amount;
        saveProgress();
        updateDisplay();
        updateCharts();
        console.log(`Updated ${type}: +${amount}`);
    }
}

function calculatePercentage(current, goal) {
    return Math.min((current / goal) * 100, 100);
}

function updateDisplay() {
    // Update progress bars
    Object.keys(todayProgress).forEach(type => {
        const current = todayProgress[type];
        const goal = DAILY_GOALS[type];
        const percentage = calculatePercentage(current, goal);
        
        if (progressBars[type]) {
            progressBars[type].style.width = `${percentage}%`;
            progressBars[type].setAttribute('aria-valuenow', percentage);
        }
        
        if (goalDisplays[type]) {
            goalDisplays[type].textContent = `${current}/${goal}`;
        }
    });
}

function initializeCharts() {
    // Initialize progress chart
    if (chartContainers.progress) {
        const ctx = chartContainers.progress.getContext('2d');
        progressChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Pomodoros',
                    data: weeklyProgress.pomodoros,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Weekly Progress'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Initialize time chart
    if (chartContainers.time) {
        const ctx = chartContainers.time.getContext('2d');
        timeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Focus Time', 'Break Time', 'Study Time'],
                datasets: [{
                    data: [todayProgress.studyTime, 30, 60],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 205, 86, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Time Distribution'
                    }
                }
            }
        });
    }
}

function updateCharts() {
    if (progressChart) {
        progressChart.data.datasets[0].data = weeklyProgress.pomodoros;
        progressChart.update();
    }
    
    if (timeChart) {
        timeChart.data.datasets[0].data = [
            todayProgress.studyTime,
            30,
            60
        ];
        timeChart.update();
    }
}

function saveProgress() {
    const data = {
        today: todayProgress,
        weekly: weeklyProgress,
        lastUpdated: new Date().toISOString()
    };
    
    localStorage.setItem('trackingProgress', JSON.stringify(data));
}

function loadProgress() {
    const saved = localStorage.getItem('trackingProgress');
    if (saved) {
        try {
            const data = JSON.parse(saved);
            todayProgress = data.today || todayProgress;
            weeklyProgress = data.weekly || weeklyProgress;
        } catch (e) {
            console.error('Error loading progress data:', e);
        }
    }
}

function resetDailyProgress() {
    todayProgress = {
        pomodoros: 0,
        studyTime: 0,
        lessons: 0,
        notes: 0
    };
    saveProgress();
    updateDisplay();
    updateCharts();
}

function getAchievements() {
    const achievements = [];
    
    if (todayProgress.pomodoros >= DAILY_GOALS.pomodoros) {
        achievements.push('🎯 Goal Crusher');
    }
    
    if (todayProgress.studyTime >= DAILY_GOALS.studyTime) {
        achievements.push('📚 Study Warrior');
    }
    
    if (todayProgress.lessons >= DAILY_GOALS.lessons) {
        achievements.push('📖 Lesson Master');
    }
    
    if (todayProgress.notes >= DAILY_GOALS.notes) {
        achievements.push('📝 Note Taker');
    }
    
    return achievements;
}

// Export for global access
window.ProgressTracking = {
    updateProgress,
    resetDailyProgress,
    getAchievements,
    getTodayProgress: () => todayProgress,
    getWeeklyProgress: () => weeklyProgress
};
