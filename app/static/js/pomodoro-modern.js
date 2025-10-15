/**
 * Modern Pomodoro Timer - Redesigned for Class Page Style
 * Clean, modern implementation with improved UX
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

let pomodoroState = {
    mode: 'pomodoro', // 'pomodoro', 'short-break', 'long-break'
    isRunning: false,
    timeLeft: 25 * 60, // seconds
    totalTime: 25 * 60, // seconds
    cycle: 1,
    currentSessionId: null,
    completedPomodoros: 0,
    tasks: [],
    settings: {
        pomodoro: 25,
        shortBreak: 5,
        longBreak: 15,
        longBreakInterval: 4,
        autoStartBreaks: true,
        soundEnabled: true
    },
    stats: {
        totalPomodoros: 0,
        totalFocusTime: 0,
        totalTasks: 0,
        totalBreaks: 0,
        todayPomodoros: 0,
        todayFocusTime: 0,
        todayTasks: 0,
        todayBreaks: 0,
        streak: 0
    }
};

const SESSION_TYPE_MAP = {
    'pomodoro': 'focus',
    'short-break': 'short_break',
    'long-break': 'long_break'
};

const TASKS_API_BASE = '/api/tasks';
const POMODORO_API_BASE = '/api/pomodoro';

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notificationText');
    
    if (notification && notificationText) {
        notificationText.textContent = message;
        notification.className = `notification show ${type}`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
}

function playNotificationSound() {
    if (pomodoroState.settings.soundEnabled) {
        // Create a simple beep sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    }
}

// ============================================================================
// TIMER FUNCTIONS
// ============================================================================

function updateTimerDisplay() {
    const timerTime = document.getElementById('timerTime');
    const timerProgress = document.getElementById('timerProgress');
    
    if (timerTime) {
        timerTime.textContent = formatTime(pomodoroState.timeLeft);
    }
    
    if (timerProgress) {
        const progress = ((pomodoroState.totalTime - pomodoroState.timeLeft) / pomodoroState.totalTime) * 100;
        timerProgress.style.background = `conic-gradient(var(--pomodoro-primary) ${progress * 3.6}deg, var(--pomodoro-border) ${progress * 3.6}deg)`;
    }
}

function updateStatusText() {
    const statusText = document.getElementById('statusText');
    const cycleInfo = document.getElementById('cycleInfo');
    
    if (statusText) {
        switch (pomodoroState.mode) {
            case 'pomodoro':
                statusText.textContent = 'Time to focus!';
                break;
            case 'short-break':
                statusText.textContent = 'Take a short break';
                break;
            case 'long-break':
                statusText.textContent = 'Take a long break';
                break;
        }
    }
    
    if (cycleInfo) {
        cycleInfo.textContent = `Cycle #${pomodoroState.cycle}`;
    }
}

function switchMode(mode, button) {
    // Update active button
    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    // Stop current timer
    if (pomodoroState.isRunning) {
        stopTimer();
    }
    
    // Update mode
    pomodoroState.mode = mode;
    
    // Set time based on mode
    switch (mode) {
        case 'pomodoro':
            pomodoroState.totalTime = pomodoroState.settings.pomodoro * 60;
            break;
        case 'short-break':
            pomodoroState.totalTime = pomodoroState.settings.shortBreak * 60;
            break;
        case 'long-break':
            pomodoroState.totalTime = pomodoroState.settings.longBreak * 60;
            break;
    }
    
    pomodoroState.timeLeft = pomodoroState.totalTime;
    updateTimerDisplay();
    updateStatusText();
    updateControlButtons();
}

function startTimer() {
    if (pomodoroState.isRunning) return;
    
    pomodoroState.isRunning = true;
    updateControlButtons();
    
    // Start session
    startPomodoroSession();
}

function pauseTimer() {
    if (!pomodoroState.isRunning) return;
    
    pomodoroState.isRunning = false;
    updateControlButtons();
}

function stopTimer() {
    pomodoroState.isRunning = false;
    updateControlButtons();
}

function resetTimer() {
    stopTimer();
    pomodoroState.timeLeft = pomodoroState.totalTime;
    updateTimerDisplay();
}

function skipTimer() {
    stopTimer();
    pomodoroState.timeLeft = 0;
    handleTimerComplete();
}

function updateControlButtons() {
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    
    if (startBtn && pauseBtn) {
        if (pomodoroState.isRunning) {
            startBtn.style.display = 'none';
            pauseBtn.style.display = 'flex';
        } else {
            startBtn.style.display = 'flex';
            pauseBtn.style.display = 'none';
        }
    }
}

function handleTimerComplete() {
    stopTimer();
    
    // Update stats
    if (pomodoroState.mode === 'pomodoro') {
        pomodoroState.completedPomodoros++;
        pomodoroState.stats.todayPomodoros++;
        pomodoroState.stats.todayFocusTime += pomodoroState.settings.pomodoro;
    } else {
        pomodoroState.stats.todayBreaks++;
    }
    
    // Show notification
    const messages = {
        'pomodoro': 'Great work! Time for a break.',
        'short-break': 'Break time is over. Ready to focus?',
        'long-break': 'Long break complete. Time to get back to work!'
    };
    
    showNotification(messages[pomodoroState.mode], 'success');
    playNotificationSound();
    
    // Auto-start next session
    if (pomodoroState.settings.autoStartBreaks && pomodoroState.mode === 'pomodoro') {
        setTimeout(() => {
            switchMode('short-break', document.querySelector('.mode-btn[data-mode="short-break"]'));
        }, 2000);
    }
    
    // Update cycle
    if (pomodoroState.mode === 'pomodoro') {
        pomodoroState.cycle++;
        if (pomodoroState.cycle % pomodoroState.settings.longBreakInterval === 0) {
            // Suggest long break
            setTimeout(() => {
                switchMode('long-break', document.querySelector('.mode-btn[data-mode="long-break"]'));
            }, 2000);
        }
    }
    
    updateStats();
    updateTimerDisplay();
}

// ============================================================================
// TASK FUNCTIONS
// ============================================================================

async function loadTasks() {
    try {
        const response = await fetch(`${TASKS_API_BASE}?limit=100`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.data) {
                pomodoroState.tasks = data.data.map(task => ({
                    id: task.id,
                    text: task.title,
                    completed: task.status === 'completed',
                    createdAt: task.created_at,
                    completedAt: task.completed_at
                }));
            }
        }
    } catch (error) {
        console.error('Failed to load tasks:', error);
    }
    
    renderTasks();
    updateTaskCount();
}

function renderTasks() {
    const taskList = document.getElementById('taskList');
    if (!taskList) return;
    
    taskList.innerHTML = '';
    
    if (pomodoroState.tasks.length === 0) {
        taskList.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-list-task" style="font-size: 2rem; opacity: 0.3;"></i>
                <p class="mt-2">No tasks yet. Add one above to get started!</p>
            </div>
        `;
        return;
    }
    
    pomodoroState.tasks.forEach(task => {
        const taskElement = createTaskElement(task);
        taskList.appendChild(taskElement);
    });
}

function createTaskElement(task) {
    const taskDiv = document.createElement('div');
    taskDiv.className = `task-item ${task.completed ? 'completed' : ''}`;
    taskDiv.innerHTML = `
        <div class="task-checkbox ${task.completed ? 'checked' : ''}" onclick="toggleTask('${task.id}')">
            ${task.completed ? '<i class="bi bi-check"></i>' : ''}
        </div>
        <div class="task-text">${task.text}</div>
        <div class="task-actions">
            <button class="task-action-btn" onclick="deleteTask('${task.id}')" title="Delete task">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    return taskDiv;
}

async function addTask() {
    const taskInput = document.getElementById('taskInput');
    const taskText = taskInput.value.trim();
    
    if (!taskText) return;
    
    try {
        const response = await fetch(TASKS_API_BASE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                title: taskText,
                task_type: 'focus',
                priority: 'medium'
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const newTask = {
                    id: data.data.id,
                    text: taskText,
                    completed: false,
                    createdAt: new Date().toISOString()
                };
                pomodoroState.tasks.unshift(newTask);
                taskInput.value = '';
                renderTasks();
                updateTaskCount();
                showNotification('Task added successfully!', 'success');
            }
        }
    } catch (error) {
        console.error('Failed to add task:', error);
        showNotification('Failed to add task', 'error');
    }
}

async function toggleTask(taskId) {
    const task = pomodoroState.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    try {
        const response = await fetch(`${TASKS_API_BASE}/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                status: task.completed ? 'pending' : 'completed'
            })
        });
        
        if (response.ok) {
            task.completed = !task.completed;
            task.completedAt = task.completed ? new Date().toISOString() : null;
            
            if (task.completed) {
                pomodoroState.stats.todayTasks++;
            }
            
            renderTasks();
            updateStats();
            showNotification(task.completed ? 'Task completed!' : 'Task reopened', 'success');
        }
    } catch (error) {
        console.error('Failed to toggle task:', error);
        showNotification('Failed to update task', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const response = await fetch(`${TASKS_API_BASE}/${taskId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            pomodoroState.tasks = pomodoroState.tasks.filter(t => t.id !== taskId);
            renderTasks();
            updateTaskCount();
            showNotification('Task deleted', 'success');
        }
    } catch (error) {
        console.error('Failed to delete task:', error);
        showNotification('Failed to delete task', 'error');
    }
}

function updateTaskCount() {
    const taskCount = document.getElementById('taskCount');
    if (taskCount) {
        const totalTasks = pomodoroState.tasks.length;
        const completedTasks = pomodoroState.tasks.filter(t => t.completed).length;
        taskCount.textContent = `${completedTasks}/${totalTasks} tasks`;
    }
}

// ============================================================================
// STATISTICS FUNCTIONS
// ============================================================================

async function loadStats() {
    try {
        // Load daily stats
        const dailyResponse = await fetch(`${POMODORO_API_BASE}/statistics/daily`, {
            credentials: 'include'
        });
        
        if (dailyResponse.ok) {
            const dailyData = await dailyResponse.json();
            if (dailyData.success && dailyData.data) {
                pomodoroState.stats.todayPomodoros = dailyData.data.today_pomodoros || 0;
                pomodoroState.stats.todayFocusTime = dailyData.data.today_focus_time || 0;
                pomodoroState.stats.todayTasks = dailyData.data.today_tasks || 0;
                pomodoroState.stats.todayBreaks = dailyData.data.today_breaks || 0;
            }
        }
        
        // Load total stats
        const totalResponse = await fetch(`${POMODORO_API_BASE}/statistics/daily-progress`, {
            credentials: 'include'
        });
        
        if (totalResponse.ok) {
            const totalData = await totalResponse.json();
            if (totalData.success && totalData.data) {
                pomodoroState.stats.totalPomodoros = totalData.data.total_pomodoros || 0;
                pomodoroState.stats.totalFocusTime = totalData.data.total_focus_time || 0;
                pomodoroState.stats.totalTasks = totalData.data.total_tasks || 0;
                pomodoroState.stats.totalBreaks = totalData.data.total_breaks || 0;
                pomodoroState.stats.streak = totalData.data.streak || 0;
            }
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
    
    updateStats();
}

function updateStats() {
    // Update today's stats
    const completedPomodoros = document.getElementById('completedPomodoros');
    const focusTime = document.getElementById('focusTime');
    const completedTasks = document.getElementById('completedTasks');
    const totalBreaks = document.getElementById('totalBreaks');
    
    if (completedPomodoros) {
        completedPomodoros.textContent = pomodoroState.stats.todayPomodoros;
    }
    
    if (focusTime) {
        const hours = Math.floor(pomodoroState.stats.todayFocusTime / 60);
        focusTime.textContent = `${hours}h`;
    }
    
    if (completedTasks) {
        completedTasks.textContent = pomodoroState.stats.todayTasks;
    }
    
    if (totalBreaks) {
        totalBreaks.textContent = pomodoroState.stats.todayBreaks;
    }
    
    // Update modal stats
    const totalPomodoros = document.getElementById('totalPomodoros');
    const totalFocusTime = document.getElementById('totalFocusTime');
    const totalTasksCompleted = document.getElementById('totalTasksCompleted');
    const streak = document.getElementById('streak');
    
    if (totalPomodoros) {
        totalPomodoros.textContent = pomodoroState.stats.totalPomodoros;
    }
    
    if (totalFocusTime) {
        const hours = Math.floor(pomodoroState.stats.totalFocusTime / 60);
        totalFocusTime.textContent = `${hours}h`;
    }
    
    if (totalTasksCompleted) {
        totalTasksCompleted.textContent = pomodoroState.stats.totalTasks;
    }
    
    if (streak) {
        streak.textContent = pomodoroState.stats.streak;
    }
}

// ============================================================================
// SESSION FUNCTIONS
// ============================================================================

async function startPomodoroSession() {
    try {
        const response = await fetch(`${POMODORO_API_BASE}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                session_type: SESSION_TYPE_MAP[pomodoroState.mode],
                duration: pomodoroState.totalTime / 60,
                task: pomodoroState.tasks.find(t => !t.completed)?.text || null
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.data) {
                pomodoroState.currentSessionId = data.data.id;
            }
        }
    } catch (error) {
        console.error('Failed to start session:', error);
    }
}

async function completePomodoroSession() {
    if (!pomodoroState.currentSessionId) return;
    
    try {
        const response = await fetch(`${POMODORO_API_BASE}/sessions/${pomodoroState.currentSessionId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        
        if (response.ok) {
            pomodoroState.currentSessionId = null;
        }
    } catch (error) {
        console.error('Failed to complete session:', error);
    }
}

// ============================================================================
// MODAL FUNCTIONS
// ============================================================================

function openSettingsModal() {
    const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
    
    // Load current settings
    document.getElementById('pomodoroTime').value = pomodoroState.settings.pomodoro;
    document.getElementById('shortBreakTime').value = pomodoroState.settings.shortBreak;
    document.getElementById('longBreakTime').value = pomodoroState.settings.longBreak;
    document.getElementById('longBreakInterval').value = pomodoroState.settings.longBreakInterval;
    document.getElementById('autoStartBreaks').checked = pomodoroState.settings.autoStartBreaks;
    document.getElementById('soundEnabled').checked = pomodoroState.settings.soundEnabled;
    
    modal.show();
}

function openStatsModal() {
    const modal = new bootstrap.Modal(document.getElementById('statsModal'));
    modal.show();
}

function saveSettings() {
    pomodoroState.settings.pomodoro = parseInt(document.getElementById('pomodoroTime').value);
    pomodoroState.settings.shortBreak = parseInt(document.getElementById('shortBreakTime').value);
    pomodoroState.settings.longBreak = parseInt(document.getElementById('longBreakTime').value);
    pomodoroState.settings.longBreakInterval = parseInt(document.getElementById('longBreakInterval').value);
    pomodoroState.settings.autoStartBreaks = document.getElementById('autoStartBreaks').checked;
    pomodoroState.settings.soundEnabled = document.getElementById('soundEnabled').checked;
    
    // Update current timer if not running
    if (!pomodoroState.isRunning) {
        switch (pomodoroState.mode) {
            case 'pomodoro':
                pomodoroState.totalTime = pomodoroState.settings.pomodoro * 60;
                break;
            case 'short-break':
                pomodoroState.totalTime = pomodoroState.settings.shortBreak * 60;
                break;
            case 'long-break':
                pomodoroState.totalTime = pomodoroState.settings.longBreak * 60;
                break;
        }
        pomodoroState.timeLeft = pomodoroState.totalTime;
        updateTimerDisplay();
    }
    
    showNotification('Settings saved!', 'success');
    bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
}

function resetStatistics() {
    if (confirm('Are you sure you want to reset all statistics? This cannot be undone.')) {
        pomodoroState.stats = {
            totalPomodoros: 0,
            totalFocusTime: 0,
            totalTasks: 0,
            totalBreaks: 0,
            todayPomodoros: 0,
            todayFocusTime: 0,
            todayTasks: 0,
            todayBreaks: 0,
            streak: 0
        };
        
        updateStats();
        showNotification('Statistics reset', 'success');
    }
}

// ============================================================================
// TIMER LOOP
// ============================================================================

function timerLoop() {
    if (pomodoroState.isRunning && pomodoroState.timeLeft > 0) {
        pomodoroState.timeLeft--;
        updateTimerDisplay();
        
        if (pomodoroState.timeLeft === 0) {
            handleTimerComplete();
            completePomodoroSession();
        }
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

function initializePomodoro() {
    console.log('🚀 Initializing Modern Pomodoro Timer...');
    
    // Load data
    loadTasks();
    loadStats();
    
    // Set up event listeners
    document.getElementById('startBtn')?.addEventListener('click', startTimer);
    document.getElementById('pauseBtn')?.addEventListener('click', pauseTimer);
    document.getElementById('resetBtn')?.addEventListener('click', resetTimer);
    document.getElementById('skipBtn')?.addEventListener('click', skipTimer);
    
    document.getElementById('addTaskBtn')?.addEventListener('click', addTask);
    document.getElementById('taskInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTask();
    });
    
    document.getElementById('saveSettings')?.addEventListener('click', saveSettings);
    document.getElementById('resetStatsBtn')?.addEventListener('click', resetStatistics);
    
    // Initialize display
    updateTimerDisplay();
    updateStatusText();
    updateControlButtons();
    updateStats();
    
    // Start timer loop
    setInterval(timerLoop, 1000);
    
    console.log('✅ Modern Pomodoro Timer initialized');
}

// ============================================================================
// SPA SUPPORT
// ============================================================================

window.onLoadPomodoro = initializePomodoro;

// Auto-initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePomodoro);
} else {
    initializePomodoro();
}
