/**
 * Pomodoro Timer - Complete Rewrite
 * Simple, working Pomodoro timer with SPA support
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

let pomodoroState = {
  mode: 'pomodoro', // 'pomodoro', 'shortBreak', 'longBreak'
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
    streak: 0,
    goalCompletionPercent: 0,
    lastDate: new Date().toDateString()
  }
};

const SESSION_TYPE_MAP = {
  pomodoro: 'focus',
  shortBreak: 'short_break',
  longBreak: 'long_break'
};

const TASKS_API_BASE = '/api/tasks';

function mapTaskFromApi(task) {
  if (!task) {
    return null;
  }

  const mapped = {
    id: task.id || null,
    text: task.title || task.text || '',
    completed: task.status === 'completed' || !!task.completed,
    createdAt: task.created_at || task.createdAt || new Date().toISOString(),
    completedAt: task.completed_at || task.completedAt || null
  };

  if (!mapped.text) {
    mapped.text = 'Untitled task';
  }

  if (mapped.completed && !mapped.completedAt) {
    mapped.completedAt = task.updated_at || mapped.createdAt;
  }

  return mapped;
}

async function createTaskOnServer(title) {
  try {
    const response = await fetch(TASKS_API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        title,
        task_type: 'focus',
        priority: 'medium'
      })
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.info('Task creation requires authentication; storing locally.');
        return null;
      }
      console.error('Failed to create task:', response.status, await response.text());
      return null;
    }

    const result = await response.json();
    if (result && result.success && result.data) {
      return mapTaskFromApi(result.data);
    }
  } catch (error) {
    console.error('Error creating task on server:', error);
  }
  return null;
}

async function updateTaskStatusOnServer(taskId, status) {
  try {
    const response = await fetch(`${TASKS_API_BASE}/${taskId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ status })
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.info('Task status update requires authentication; keeping local state.');
        return null;
      }
      console.error('Failed to update task status:', response.status, await response.text());
      return null;
    }

    const result = await response.json();
    if (result && result.success && result.data) {
      return mapTaskFromApi(result.data);
    }
  } catch (error) {
    console.error('Error updating task status on server:', error);
  }
  return null;
}

async function deleteTaskOnServer(taskId) {
  try {
    const response = await fetch(`${TASKS_API_BASE}/${taskId}`, {
      method: 'DELETE',
      credentials: 'include'
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.info('Task deletion requires authentication; removing locally only.');
        return false;
      }
      console.error('Failed to delete task:', response.status, await response.text());
      return false;
    }

    const result = await response.json().catch(() => ({ success: true }));
    return Boolean(result && result.success);
  } catch (error) {
    console.error('Error deleting task on server:', error);
  }
  return false;
}

async function syncTasksFromServer() {
  try {
    const response = await fetch(`${TASKS_API_BASE}?limit=100`, {
      credentials: 'include'
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.info('Task API requires authentication; using local task state.');
        return false;
      }
      console.error('Failed to fetch tasks:', response.status, await response.text());
      return false;
    }

    const result = await response.json();
    if (result && result.success && Array.isArray(result.data)) {
      const mappedTasks = result.data.map(mapTaskFromApi).filter(Boolean);
      pomodoroState.tasks = mappedTasks;
      updateTaskStatsFromLocal();
      updateTaskList();
      updateStats();
      saveState();
      return true;
    }
  } catch (error) {
    console.error('Error syncing tasks from server:', error);
  }
  return false;
}

function updateTaskStatsFromLocal() {
  const completedTasks = pomodoroState.tasks.filter(task => task.completed).length;
  pomodoroState.stats.totalTasks = completedTasks;

  const todayString = new Date().toISOString().split('T')[0];
  const todayCompleted = pomodoroState.tasks.filter(task => {
    if (!task.completed) {
      return false;
    }
    if (!task.completedAt) {
      return false;
    }
    return task.completedAt.startsWith(todayString);
  }).length;

  pomodoroState.stats.todayTasks = todayCompleted;
}

async function ensureSessionForCurrentMode() {
  if (pomodoroState.currentSessionId) {
    return true;
  }

  const sessionType = SESSION_TYPE_MAP[pomodoroState.mode];
  if (!sessionType) {
    return true;
  }

  const newSession = await createSessionInDatabase(sessionType);
  if (newSession && newSession.id) {
    pomodoroState.currentSessionId = newSession.id;
    saveState();
    return true;
  }

  console.error('Unable to create Pomodoro session in database.');
  return false;
}

async function createSessionInDatabase(sessionType) {
  const durationMinutes = Math.max(1, Math.round(pomodoroState.totalTime / 60));
  const payload = {
    session_type: sessionType,
    duration: durationMinutes,
    auto_start_next: pomodoroState.settings.autoStartBreaks,
    notification_enabled: true,
    sound_enabled: pomodoroState.settings.soundEnabled
  };

  try {
    const response = await fetch('/api/pomodoro/session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const result = await response.json();
      if (result && result.success) {
        console.log('✅ Session created in database:', result.session?.id);
        return result.session;
      }
    } else {
      console.error('Failed to create session:', response.status);
    }
  } catch (error) {
    console.error('Error creating session:', error);
  }

  return null;
}

async function endSessionInDatabase() {
  if (!pomodoroState.currentSessionId) {
    return;
  }

  try {
    const response = await fetch(`/api/pomodoro/session/${pomodoroState.currentSessionId}/end`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    });

    if (response.ok) {
      const result = await response.json();
      if (result && result.success) {
        console.log('✅ Session ended in database:', pomodoroState.currentSessionId);
      }
    } else {
      console.error('Failed to end session:', response.status);
    }
  } catch (error) {
    console.error('Error ending session:', error);
  }
}

async function interruptSessionInDatabase() {
  if (!pomodoroState.currentSessionId) {
    return;
  }

  try {
    const response = await fetch(`/api/pomodoro/session/${pomodoroState.currentSessionId}/interrupt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    });

    if (response.ok) {
      const result = await response.json();
      if (result && result.success) {
        console.log('⚠️ Session interrupted in database:', pomodoroState.currentSessionId);
      }
    } else {
      console.error('Failed to interrupt session:', response.status);
    }
  } catch (error) {
    console.error('Error interrupting session:', error);
  }
}

function applyTimerStats(timerStats) {
  if (!timerStats) {
    return;
  }

  pomodoroState.stats.totalPomodoros = Number(timerStats.total_pomodoros) || 0;
  pomodoroState.stats.totalFocusTime = Number(timerStats.total_focus_minutes) || 0;
  pomodoroState.stats.totalTasks = Number(timerStats.total_tasks_completed) || 0;
  pomodoroState.stats.streak = Number(timerStats.streak) || 0;
  pomodoroState.stats.totalBreaks = Number(timerStats.total_break_sessions) || 0;
}

function applyDailyProgress(progress) {
  if (!progress) {
    return;
  }

  pomodoroState.stats.todayPomodoros = Number(progress.completed_sessions) || 0;
  pomodoroState.stats.todayFocusTime = Number(progress.focus_minutes) || 0;
  pomodoroState.stats.todayTasks = Number(progress.tasks_completed) || 0;
  pomodoroState.stats.todayBreaks = Number(progress.break_sessions) || 0;
  pomodoroState.stats.goalCompletionPercent = Number(progress.goal_completion_percent) || 0;
  pomodoroState.completedPomodoros = pomodoroState.stats.todayPomodoros;
}

async function refreshServerStats() {
  const todayString = new Date().toISOString().split('T')[0];

  try {
    await fetch('/api/pomodoro/statistics/daily', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ date: todayString })
    });
  } catch (error) {
    console.error('Error recalculating daily pomodoro statistics:', error);
  }

  try {
    const [timerResponse, dailyResponse] = await Promise.all([
      fetch('/api/pomodoro/statistics/timer', { credentials: 'include' }),
      fetch('/api/pomodoro/statistics/daily-progress', { credentials: 'include' })
    ]);

    if ((timerResponse && timerResponse.status === 401) || (dailyResponse && dailyResponse.status === 401)) {
      console.warn('Pomodoro statistics endpoints require authentication.');
      return;
    }

    if (timerResponse && timerResponse.ok) {
      const timerJson = await timerResponse.json();
      if (timerJson && timerJson.success) {
        applyTimerStats(timerJson.stats);
      }
    }

    if (dailyResponse && dailyResponse.ok) {
      const dailyJson = await dailyResponse.json();
      if (dailyJson && dailyJson.success) {
        applyDailyProgress(dailyJson.progress);
      }
    }

    updateStats();
    saveState();
  } catch (error) {
    console.error('Error fetching pomodoro statistics:', error);
  }
}

function clearCurrentSession() {
  pomodoroState.currentSessionId = null;
}

// Timer variables
let interval = null;
let globalTimer = null;
let lastTick = Date.now();
let isInitialized = false;

// ============================================================================
// CORE FUNCTIONS
// ============================================================================

// Get current mode time
function getModeTime() {
  switch (pomodoroState.mode) {
    case 'pomodoro': return pomodoroState.settings.pomodoro * 60;
    case 'shortBreak': return pomodoroState.settings.shortBreak * 60;
    case 'longBreak': return pomodoroState.settings.longBreak * 60;
    default: return 25 * 60;
  }
}

// Switch to next mode
function nextMode() {
  console.log('🔄 Moving to next mode...');
  console.log('🔄 Current mode:', pomodoroState.mode, 'Cycle:', pomodoroState.cycle);
  
  if (pomodoroState.mode === 'pomodoro') {
    pomodoroState.cycle++;
    if (pomodoroState.cycle % pomodoroState.settings.longBreakInterval === 0) {
      pomodoroState.mode = 'longBreak';
      console.log('🔄 Switching to long break (cycle', pomodoroState.cycle, ')');
    } else {
      pomodoroState.mode = 'shortBreak';
      console.log('🔄 Switching to short break (cycle', pomodoroState.cycle, ')');
    }
  } else {
    pomodoroState.mode = 'pomodoro';
    console.log('🔄 Switching back to pomodoro');
  }
  
  // Reset timer for new mode
  pomodoroState.timeLeft = getModeTime();
  pomodoroState.totalTime = getModeTime();
  pomodoroState.isRunning = false;
  clearCurrentSession();
  
  console.log('✅ Next mode set to:', pomodoroState.mode, 'with', pomodoroState.timeLeft, 'seconds');
}

// Complete current session
function completeSession() {
  if (pomodoroState.mode === 'pomodoro') {
    pomodoroState.completedPomodoros++;
    pomodoroState.stats.totalPomodoros++;
    pomodoroState.stats.todayPomodoros++;
    pomodoroState.stats.totalFocusTime += pomodoroState.settings.pomodoro;
    pomodoroState.stats.todayFocusTime += pomodoroState.settings.pomodoro;
  } else {
    pomodoroState.stats.todayBreaks++;
  }
}

// ============================================================================
// TIMER FUNCTIONS
// ============================================================================

// Start timer
async function startTimer() {
  console.log('🎯 startTimer called, current state:', {
    isRunning: pomodoroState.isRunning,
    timeLeft: pomodoroState.timeLeft
  });
  
  if (pomodoroState.isRunning) {
    console.log('⏸️ Timer is running, calling pauseTimer()');
    pauseTimer();
    return;
  }

  const sessionReady = await ensureSessionForCurrentMode();
  if (!sessionReady) {
    console.warn('Unable to start timer because session could not be created.');
    return;
  }

  console.log('⏰ Starting Pomodoro timer...');
  console.log('⏰ Current timeLeft:', pomodoroState.timeLeft);
  pomodoroState.isRunning = true;
  lastTick = Date.now();
  
  // Start local interval for UI updates
  startLocalInterval();
  
  // Start global timer for background operation
  startGlobalTimer();
  
  // Update button state
  updateButtons();
  
  saveState();
}

// Pause timer
function pauseTimer() {
  console.log('⏸️ Pausing Pomodoro timer...');
  console.log('⏸️ Before pause - isRunning:', pomodoroState.isRunning);
  pomodoroState.isRunning = false;
  console.log('⏸️ After pause - isRunning:', pomodoroState.isRunning);
  stopAllTimers();
  updateButtons(); // Update button state
  saveState();
}

// Reset timer
async function resetTimer() {
  console.log('🔄 Resetting Pomodoro timer...');
  console.log('🔄 Current mode:', pomodoroState.mode);
  
  if (pomodoroState.currentSessionId) {
    await interruptSessionInDatabase();
    clearCurrentSession();
    await refreshServerStats();
    saveState();
  }
  
  pomodoroState.isRunning = false;
  pomodoroState.timeLeft = getModeTime();
  pomodoroState.totalTime = getModeTime();
  
  console.log('🔄 Reset to:', pomodoroState.timeLeft, 'seconds');
  
  stopAllTimers();
  updateButtons(); // Update button state
  updateDisplay(); // Update display
  saveState();
}

// Skip current session
async function skipTimer() {
  console.log('⏭️ Skipping current session...');
  console.log('⏭️ Current mode:', pomodoroState.mode);
  
  // Stop current timer
  pomodoroState.isRunning = false;
  stopAllTimers();
  
  if (pomodoroState.currentSessionId) {
    await interruptSessionInDatabase();
    clearCurrentSession();
    await refreshServerStats();
    saveState();
  }
  
  // Move to next mode
  nextMode();
  
  console.log('⏭️ Switched to mode:', pomodoroState.mode);
  
  updateButtons(); // Update button state
  updateAll(); // Update all UI elements
  saveState();
}

// Start local interval for UI updates
function startLocalInterval() {
  if (interval) {
    clearInterval(interval);
  }
  
  interval = setInterval(() => {
    if (pomodoroState.isRunning) {
      // Only update display to avoid excessive UI updates
      updateDisplay();
    }
  }, 100);
}

// Start global timer for background operation
function startGlobalTimer() {
  if (globalTimer) {
    clearInterval(globalTimer);
  }
  
  globalTimer = setInterval(() => {
    if (pomodoroState.isRunning) {
      const now = Date.now();
      const delta = Math.floor((now - lastTick) / 1000);
      
      if (delta >= 1) {
        if (pomodoroState.timeLeft > 0) {
          pomodoroState.timeLeft = Math.max(0, pomodoroState.timeLeft - delta);
          lastTick = now;
          saveState();
          
          console.log('⏰ Timer tick:', pomodoroState.timeLeft, 'seconds left');
          
          // Update UI immediately (updateDisplay already calls updateButtons via updateAll)
          updateDisplay();
          
          if (pomodoroState.timeLeft === 0) {
            timerComplete().catch(error => {
              console.error('Error completing timer:', error);
            });
          }
        }
      }
    }
  }, 1000);
}

// Timer completed
async function timerComplete() {
  console.log('🔔 Timer completed!');
  pomodoroState.isRunning = false;
  completeSession();
  await endSessionInDatabase();
  await refreshServerStats();
  clearCurrentSession();
  saveState();
  
  // Play sound if enabled
  if (pomodoroState.settings.soundEnabled) {
    playSound();
  }
  
  // Auto-start next session if enabled
  if (pomodoroState.settings.autoStartBreaks && pomodoroState.mode === 'pomodoro') {
    setTimeout(() => {
      nextMode();
      startTimer();
    }, 1000);
  } else {
    nextMode();
  }
  
  stopAllTimers();
  updateButtons(); // Update button state
  saveState();
}

// Stop all timers
function stopAllTimers() {
  if (interval) {
    clearInterval(interval);
    interval = null;
  }
  if (globalTimer) {
    clearInterval(globalTimer);
    globalTimer = null;
  }
}

// Play completion sound
function playSound() {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.2);
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  } catch (e) {
    console.error('Sound playback failed:', e);
  }
}

// ============================================================================
// UI FUNCTIONS
// ============================================================================

// Update timer display
function updateDisplay() {
  const timeDisplay = document.getElementById('timeDisplay');
  if (!timeDisplay) {
    console.log('❌ timeDisplay element not found');
    return;
  }
  
  const minutes = Math.floor(pomodoroState.timeLeft / 60);
  const seconds = pomodoroState.timeLeft % 60;
  const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  
  console.log('🔄 Updating display:', timeString, '(timeLeft:', pomodoroState.timeLeft, 'seconds)');
  timeDisplay.textContent = timeString;
  
  // Update progress bar
  const progressBar = document.getElementById('progressBar');
  if (progressBar) {
    const progress = ((pomodoroState.totalTime - pomodoroState.timeLeft) / pomodoroState.totalTime) * 100;
    progressBar.style.width = `${progress}%`;
    console.log('🔄 Progress bar updated to', progress + '%');
  }
}

// Update mode display
function updateModeDisplay() {
  // Update status text instead of modeDisplay (which doesn't exist in HTML)
  const statusText = document.getElementById('statusText');
  if (statusText) {
    const statusMessages = {
      'pomodoro': 'Time to focus!',
      'shortBreak': 'Take a short break',
      'longBreak': 'Take a long break'
    };
    statusText.textContent = statusMessages[pomodoroState.mode] || 'Time to focus!';
  }
}

// Update button states
function updateButtons() {
  const startBtn = document.getElementById('startBtn');
  if (startBtn) {
    const newText = pomodoroState.isRunning ? 'Pause' : 'Start';
    const newClass = pomodoroState.isRunning ? 'btn btn-warning' : 'btn btn-success';
    
    console.log('🔄 Updating button:', {
      isRunning: pomodoroState.isRunning,
      newText: newText,
      newClass: newClass
    });
    
    startBtn.textContent = newText;
    startBtn.className = newClass;
  } else {
    console.warn('⚠️ startBtn element not found');
  }
}

// Update mode tabs
function updateModeTabs() {
  console.log('🔄 Updating mode tabs for mode:', pomodoroState.mode);
  
  // Remove active class from all tabs - try both ID and data-mode selectors
  const tabSelectors = [
    { id: 'pomodoroTab', dataMode: 'pomodoro' },
    { id: 'shortBreakTab', dataMode: 'short' },
    { id: 'longBreakTab', dataMode: 'long' }
  ];
  
  tabSelectors.forEach(({ id, dataMode }) => {
    let tab = document.getElementById(id);
    if (!tab) {
      tab = document.querySelector(`[data-mode="${dataMode}"]`);
    }
    if (tab) {
      tab.classList.remove('active');
      console.log('🔄 Removed active class from', id || dataMode);
    }
  });
  
  // Add active class to current mode tab
  const modeMap = {
    'pomodoro': { id: 'pomodoroTab', dataMode: 'pomodoro' },
    'shortBreak': { id: 'shortBreakTab', dataMode: 'short' },
    'longBreak': { id: 'longBreakTab', dataMode: 'long' }
  };
  
  const currentMode = modeMap[pomodoroState.mode];
  if (currentMode) {
    let currentTab = document.getElementById(currentMode.id);
    if (!currentTab) {
      currentTab = document.querySelector(`[data-mode="${currentMode.dataMode}"]`);
    }
    
    if (currentTab) {
      currentTab.classList.add('active');
      console.log('✅ Added active class to', currentMode.id || currentMode.dataMode);
    } else {
      console.warn('⚠️ Current tab not found:', currentMode.id, 'or', currentMode.dataMode);
    }
  }
}

// Update cycle information
function updateCycleInfo() {
  const cycleInfo = document.getElementById('cycleInfo');
  if (cycleInfo) {
    cycleInfo.textContent = `Cycle #${pomodoroState.cycle}`;
  }
  
  const statusText = document.getElementById('statusText');
  if (statusText) {
    let status = '';
    if (pomodoroState.mode === 'pomodoro') {
      status = 'Time to focus!';
    } else if (pomodoroState.mode === 'shortBreak') {
      status = 'Short break time!';
    } else if (pomodoroState.mode === 'longBreak') {
      status = 'Long break time!';
    }
    statusText.textContent = status;
  }
}

// Update stats display
function updateStats() {
  const stats = pomodoroState.stats;
  
  console.log('📊 Updating stats:', stats);
  
  // Update total stats (in stats dialog)
  const totalPomodoros = document.getElementById('totalPomodoros');
  if (totalPomodoros) {
    totalPomodoros.textContent = stats.totalPomodoros;
  }
  
  const totalFocusTime = document.getElementById('totalFocusTime');
  if (totalFocusTime) {
    totalFocusTime.textContent = formatTime(stats.totalFocusTime * 60);
  }
  
  const totalTasks = document.getElementById('totalTasksCompleted');
  if (totalTasks) {
    totalTasks.textContent = stats.totalTasks;
  }

  const streakElement = document.getElementById('streak');
  if (streakElement) {
    streakElement.textContent = stats.streak ?? 0;
  }
  
  // Update today's stats (in main display)
  const todayPomodoros = document.getElementById('completedPomodoros');
  if (todayPomodoros) {
    todayPomodoros.textContent = stats.todayPomodoros;
  }
  
  const todayFocusTime = document.getElementById('focusTime');
  if (todayFocusTime) {
    todayFocusTime.textContent = formatTime(stats.todayFocusTime * 60);
  }
  
  const todayTasks = document.getElementById('completedTasks');
  if (todayTasks) {
    todayTasks.textContent = stats.todayTasks;
  }
  
  const todayBreaks = document.getElementById('totalBreaks');
  if (todayBreaks) {
    todayBreaks.textContent = stats.todayBreaks;
  }
}

// Update task list
function updateTaskList() {
  const taskList = document.getElementById('taskList');
  if (!taskList) {
    return;
  }

  taskList.innerHTML = '';

  pomodoroState.tasks.forEach((task, index) => {
    const taskElement = document.createElement('li');
    taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;

    // Task content (checkbox + text)
    const taskContent = document.createElement('div');
    taskContent.className = 'task-content';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = Boolean(task.completed);
    checkbox.addEventListener('change', () => {
      toggleTask(index).catch(error => {
        console.error('Error toggling task:', error);
      });
    });

    const taskText = document.createElement('span');
    taskText.className = 'task-text';
    taskText.textContent = task.text;

    taskContent.appendChild(checkbox);
    taskContent.appendChild(taskText);

    // Task actions (delete)
    const taskActions = document.createElement('div');
    taskActions.className = 'task-actions';

    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn btn-sm btn-outline-danger';
    removeBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
    removeBtn.addEventListener('click', () => {
      removeTask(index).catch(error => {
        console.error('Error removing task:', error);
      });
    });
    taskActions.appendChild(removeBtn);

    taskElement.appendChild(taskContent);
    taskElement.appendChild(taskActions);
    taskList.appendChild(taskElement);
  });

  const taskCount = document.getElementById('taskCount');
  if (taskCount) {
    const count = pomodoroState.tasks.length;
    taskCount.textContent = `${count} ${count === 1 ? 'task' : 'tasks'}`;
  }
}

// Format time for display
function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
}

// Update all UI elements
function updateAll() {
  updateDisplay();
  updateModeDisplay();
  updateButtons();
  updateModeTabs();
  updateStats();
  updateTaskList();
  updateCycleInfo();
}

// ============================================================================
// TASK FUNCTIONS
// ============================================================================

// Add new task
async function addTask() {
  const taskInput = document.getElementById('taskInput');
  if (!taskInput) {
    return;
  }

  const text = taskInput.value.trim();
  if (!text) {
    return;
  }

  const localTask = {
    id: null,
    text,
    completed: false,
    createdAt: new Date().toISOString(),
    completedAt: null
  };

  taskInput.value = '';

  let createdTask = null;
  try {
    createdTask = await createTaskOnServer(text);
  } catch (error) {
    console.error('Error while creating task:', error);
  }

  const taskToStore = createdTask || localTask;
  pomodoroState.tasks.push(taskToStore);

  updateTaskStatsFromLocal();
  updateTaskList();
  updateStats();
  saveState();

  if (createdTask) {
    await refreshServerStats();
  }
}

async function toggleTask(index) {
  if (index < 0 || index >= pomodoroState.tasks.length) {
    return;
  }

  const task = pomodoroState.tasks[index];
  const newCompleted = !task.completed;
  const desiredStatus = newCompleted ? 'completed' : 'pending';

  let updatedTask = null;
  let serverSynced = false;

  try {
    if (task.id) {
      updatedTask = await updateTaskStatusOnServer(task.id, desiredStatus);
      serverSynced = Boolean(updatedTask);
    } else {
      const createdTask = await createTaskOnServer(task.text);
      if (createdTask && createdTask.id) {
        pomodoroState.tasks[index] = { ...task, ...createdTask };
        updatedTask = await updateTaskStatusOnServer(createdTask.id, desiredStatus);
        serverSynced = Boolean(updatedTask);
      }
    }
  } catch (error) {
    console.error('Error syncing task status:', error);
  }

  if (updatedTask) {
    pomodoroState.tasks[index] = {
      ...pomodoroState.tasks[index],
      ...updatedTask
    };
  } else {
    pomodoroState.tasks[index].completed = newCompleted;
    pomodoroState.tasks[index].completedAt = newCompleted ? new Date().toISOString() : null;
  }

  updateTaskStatsFromLocal();
  updateTaskList();
  updateStats();
  saveState();

  if (serverSynced) {
    await refreshServerStats();
  }
}

async function removeTask(index) {
  if (index < 0 || index >= pomodoroState.tasks.length) {
    return;
  }

  const task = pomodoroState.tasks[index];
  let serverDeleted = false;

  if (task.id) {
    try {
      serverDeleted = await deleteTaskOnServer(task.id);
    } catch (error) {
      console.error('Error deleting task on server:', error);
    }
  }

  pomodoroState.tasks.splice(index, 1);

  updateTaskStatsFromLocal();
  updateTaskList();
  updateStats();
  saveState();

  if (serverDeleted) {
    await refreshServerStats();
  }
}

// ============================================================================
// SETTINGS FUNCTIONS
// ============================================================================

// Show settings dialog
function showSettings() {
  const settingsDialog = document.getElementById('settingsDialog');
  if (!settingsDialog) return;
  
  // Populate settings form
  const settings = pomodoroState.settings;
  document.getElementById('pomodoroTime').value = settings.pomodoro;
  document.getElementById('shortBreakTime').value = settings.shortBreak;
  document.getElementById('longBreakTime').value = settings.longBreak;
  document.getElementById('longBreakInterval').value = settings.longBreakInterval;
  document.getElementById('autoStartBreaks').checked = settings.autoStartBreaks;
  document.getElementById('soundEnabled').checked = settings.soundEnabled;
  
  settingsDialog.showModal();
}

// Save settings
async function handleSaveSettings() {
  const settings = {
    pomodoro: parseInt(document.getElementById('pomodoroTime').value) || 25,
    shortBreak: parseInt(document.getElementById('shortBreakTime').value) || 5,
    longBreak: parseInt(document.getElementById('longBreakTime').value) || 15,
    longBreakInterval: parseInt(document.getElementById('longBreakInterval').value) || 4,
    autoStartBreaks: document.getElementById('autoStartBreaks').checked,
    soundEnabled: document.getElementById('soundEnabled').checked
  };
  
  pomodoroState.settings = settings;
  await resetTimer();
  document.getElementById('settingsDialog').close();
  saveState();
  updateAll();
}

// Show stats dialog
function showStats() {
  const statsDialog = document.getElementById('statsDialog');
  if (!statsDialog) return;
  updateStats();
  statsDialog.showModal();
}

// Reset stats
function resetStats() {
  if (confirm('Are you sure you want to reset all statistics?')) {
    pomodoroState.stats = {
      totalPomodoros: 0,
      totalFocusTime: 0,
      totalTasks: 0,
      todayPomodoros: 0,
      todayFocusTime: 0,
      todayTasks: 0,
      todayBreaks: 0,
      lastDate: new Date().toDateString()
    };
    saveState();
    updateStats();
  }
}

// ============================================================================
// MODE FUNCTIONS
// ============================================================================

// Switch to different mode
function switchMode(mode) {
  console.log('🔄 switchMode called with mode:', mode);
  console.log('🔄 Current mode:', pomodoroState.mode);
  console.log('🔄 Mode change needed:', pomodoroState.mode !== mode);
  
  if (pomodoroState.mode !== mode) {
    console.log('🔄 Performing mode switch...');
    
    // Stop current timer if running
    if (pomodoroState.isRunning) {
      console.log('⏸️ Stopping current timer before mode switch');
      pomodoroState.isRunning = false;
      stopAllTimers();
    }
    
    pomodoroState.mode = mode;
    
    // Reset timer for new mode
    pomodoroState.timeLeft = getModeTime();
    pomodoroState.totalTime = getModeTime();
    clearCurrentSession();
    
    console.log('✅ Mode switched to', mode, 'with', pomodoroState.timeLeft, 'seconds');
    console.log('✅ Timer display should show:', Math.floor(pomodoroState.timeLeft / 60) + ':' + (pomodoroState.timeLeft % 60).toString().padStart(2, '0'));
    
    updateAll();
    saveState();
    
    console.log('✅ Mode switch completed');
  } else {
    console.log('⚠️ Already in', mode, 'mode, no change needed');
  }
}

// ============================================================================
// STATE PERSISTENCE
// ============================================================================

// Save state to localStorage
function saveState() {
  try {
    const stateToSave = { 
      ...pomodoroState,
      lastTick: Date.now() // Add timestamp for sync
    };
    localStorage.setItem('pomodoroState', JSON.stringify(stateToSave));
    console.log('💾 Pomodoro state saved');
  } catch (e) {
    console.error('Error saving pomodoro state:', e);
  }
}

// Load state from localStorage
function loadState() {
  try {
    const savedState = localStorage.getItem('pomodoroState');
    if (savedState) {
      const parsedState = JSON.parse(savedState);
      Object.assign(pomodoroState, parsedState);

      if (Array.isArray(parsedState.tasks)) {
        pomodoroState.tasks = parsedState.tasks.map((task) => {
          const mapped = {
            id: task.id || task.task_id || null,
            text: task.text || task.title || '',
            completed: Boolean(task.completed) || task.status === 'completed',
            createdAt: task.createdAt || task.created_at || new Date().toISOString(),
            completedAt: task.completedAt || task.completed_at || null
          };

          if (!mapped.text) {
            mapped.text = 'Untitled task';
          }

          if (mapped.completed && !mapped.completedAt) {
            mapped.completedAt = new Date().toISOString();
          }

          return mapped;
        });
      } else {
        pomodoroState.tasks = [];
      }

      updateTaskStatsFromLocal();
      console.log('📂 Pomodoro state loaded');
      return true;
    }
  } catch (e) {
    console.error('Error loading pomodoro state:', e);
  }
  return false;
}

// Check for new day and reset daily stats
function checkNewDay() {
  const today = new Date().toDateString();
  if (pomodoroState.stats.lastDate !== today) {
    console.log('📅 New day detected, resetting daily stats');
    pomodoroState.stats.todayPomodoros = 0;
    pomodoroState.stats.todayFocusTime = 0;
    pomodoroState.stats.todayTasks = 0;
    pomodoroState.stats.todayBreaks = 0;
    pomodoroState.stats.lastDate = today;
    saveState();
  }
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

// Remove existing event listeners to prevent duplicates
function removeEventListeners() {
  console.log('🧹 Removing existing event listeners...');
  
  // Clone elements to remove all event listeners
  const elements = [
    'startBtn', 'resetBtn', 'skipBtn', 'pomodoroTab', 'shortBreakTab', 'longBreakTab',
  'addTaskBtn', 'taskInput', 'settingsBtn', 'closeSettings', 'saveSettings',
  'statsBtn', 'closeStats', 'closeStatsBtn', 'resetStatsBtn'
  ];
  
  elements.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      const newElement = element.cloneNode(true);
      element.parentNode.replaceChild(newElement, element);
    }
  });
}

// Setup all event listeners
function setupEventListeners() {
  console.log('🔗 Setting up event listeners...');
  
  // Remove existing event listeners first to prevent duplicates
  removeEventListeners();
  
  // Timer controls
  const startBtn = document.getElementById('startBtn');
  if (startBtn) {
    console.log('🔗 Adding click listener to startBtn');
    startBtn.addEventListener('click', startTimer);
  } else {
    console.warn('⚠️ startBtn not found when setting up event listeners');
  }
  
  const resetBtn = document.getElementById('resetBtn');
  if (resetBtn) {
    console.log('🔗 Adding click listener to resetBtn');
    resetBtn.addEventListener('click', resetTimer);
  } else {
    console.warn('⚠️ resetBtn not found when setting up event listeners');
  }
  
  const skipBtn = document.getElementById('skipBtn');
  if (skipBtn) {
    console.log('🔗 Adding click listener to skipBtn');
    skipBtn.addEventListener('click', skipTimer);
  } else {
    console.warn('⚠️ skipBtn not found when setting up event listeners');
  }
  
  // Mode tabs - try both ID and data-mode selectors
  let pomodoroTab = document.getElementById('pomodoroTab');
  if (!pomodoroTab) {
    pomodoroTab = document.querySelector('[data-mode="pomodoro"]');
  }
  if (pomodoroTab) {
    console.log('🔗 Adding click listener to pomodoroTab');
    pomodoroTab.addEventListener('click', (e) => {
      console.log('🖱️ Pomodoro tab clicked!');
      e.preventDefault();
      switchMode('pomodoro');
    });
  } else {
    console.warn('⚠️ pomodoroTab not found when setting up event listeners');
  }
  
  let shortBreakTab = document.getElementById('shortBreakTab');
  if (!shortBreakTab) {
    shortBreakTab = document.querySelector('[data-mode="short"]');
  }
  if (shortBreakTab) {
    console.log('🔗 Adding click listener to shortBreakTab');
    shortBreakTab.addEventListener('click', (e) => {
      console.log('🖱️ Short Break tab clicked!');
      e.preventDefault();
      switchMode('shortBreak');
    });
  } else {
    console.warn('⚠️ shortBreakTab not found when setting up event listeners');
  }
  
  let longBreakTab = document.getElementById('longBreakTab');
  if (!longBreakTab) {
    longBreakTab = document.querySelector('[data-mode="long"]');
  }
  if (longBreakTab) {
    console.log('🔗 Adding click listener to longBreakTab');
    longBreakTab.addEventListener('click', (e) => {
      console.log('🖱️ Long Break tab clicked!');
      e.preventDefault();
      switchMode('longBreak');
    });
  } else {
    console.warn('⚠️ longBreakTab not found when setting up event listeners');
  }
  
  // Tasks
  const addTaskBtn = document.getElementById('addTaskBtn');
  if (addTaskBtn) {
    addTaskBtn.addEventListener('click', addTask);
  }
  
  const taskInput = document.getElementById('taskInput');
  if (taskInput) {
    taskInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        addTask();
      }
    });
  }
  
  // Settings
  const settingsBtn = document.getElementById('settingsBtn');
  if (settingsBtn) {
    settingsBtn.addEventListener('click', showSettings);
  }
  
  const closeSettings = document.getElementById('closeSettings');
  if (closeSettings) {
    closeSettings.addEventListener('click', () => {
      document.getElementById('settingsDialog').close();
    });
  }
  
  const saveSettingsBtn = document.getElementById('saveSettings');
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener('click', (event) => {
      event.preventDefault();
      handleSaveSettings();
    });
  }
  
  // Stats
  const statsBtn = document.getElementById('statsBtn');
  if (statsBtn) {
    statsBtn.addEventListener('click', showStats);
  }
  
  const closeStats = document.getElementById('closeStats');
  if (closeStats) {
    closeStats.addEventListener('click', () => {
      document.getElementById('statsDialog').close();
    });
  }
  
  const closeStatsBtn = document.getElementById('closeStatsBtn');
  if (closeStatsBtn) {
    closeStatsBtn.addEventListener('click', () => {
      document.getElementById('statsDialog').close();
    });
  }
  
  const resetStatsBtn = document.getElementById('resetStatsBtn');
  if (resetStatsBtn) {
    resetStatsBtn.addEventListener('click', resetStats);
  }
  
  console.log('✅ Event listeners setup complete');
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// Initialize the application
function initialize() {
  console.log('🚀 Initializing Pomodoro App...');
  
  // Prevent multiple initializations
  if (isInitialized) {
    console.log('⚠️ Pomodoro already initialized, skipping...');
    return;
  }
  
  // Load saved state
  loadState();
  
  // Check for new day
  checkNewDay();
  updateTaskStatsFromLocal();
  
  // Display current settings
  console.log('🍅 Pomodoro Settings:', {
    pomodoro: pomodoroState.settings.pomodoro + ' minutes',
    shortBreak: pomodoroState.settings.shortBreak + ' minutes', 
    longBreak: pomodoroState.settings.longBreak + ' minutes',
    longBreakInterval: 'every ' + pomodoroState.settings.longBreakInterval + ' pomodoros',
    autoStartBreaks: pomodoroState.settings.autoStartBreaks,
    soundEnabled: pomodoroState.settings.soundEnabled
  });
  
  console.log('🔄 Current State:', {
    mode: pomodoroState.mode,
    cycle: pomodoroState.cycle,
    timeLeft: pomodoroState.timeLeft + ' seconds',
    isRunning: pomodoroState.isRunning
  });
  
  // Check if all required DOM elements exist
  const requiredElements = [
    { id: 'timeDisplay' },
    { id: 'startBtn' },
    { id: 'resetBtn' },
    { id: 'skipBtn' },
    { id: 'pomodoroTab', dataMode: 'pomodoro' },
    { id: 'shortBreakTab', dataMode: 'short' },
    { id: 'longBreakTab', dataMode: 'long' }
  ];
  
  const missingElements = [];
  requiredElements.forEach(({ id, dataMode }) => {
    let element = document.getElementById(id);
    if (!element && dataMode) {
      element = document.querySelector(`[data-mode="${dataMode}"]`);
    }
    if (!element) {
      missingElements.push(id || dataMode);
    }
  });
  
  if (missingElements.length > 0) {
    console.error('❌ Missing required elements:', missingElements);
  } else {
    console.log('✅ All required elements found');
  }
  
  // Debug: Show found elements
  console.log('🔍 Found elements:');
  requiredElements.forEach(({ id, dataMode }) => {
    let element = document.getElementById(id);
    if (!element && dataMode) {
      element = document.querySelector(`[data-mode="${dataMode}"]`);
    }
    if (element) {
      console.log(`✅ ${id || dataMode}:`, element.textContent || element.className);
    }
  });
  
  // Setup event listeners
  setupEventListeners();
  
  // Update UI
  updateAll();
  syncTasksFromServer().then((synced) => {
    if (synced) {
      updateStats();
    }
  });
  refreshServerStats().catch(error => {
    console.error('Error syncing pomodoro statistics on init:', error);
  });
  
  isInitialized = true;
  console.log('✅ Pomodoro App initialized');
}

// Cleanup when leaving page
function cleanup() {
  console.log('🧹 Cleaning up Pomodoro App...');
  
  // Don't stop global timer - let it continue running
  // Only stop local interval for UI updates
  if (interval) {
    clearInterval(interval);
    interval = null;
  }
  
  // Remove event listeners to prevent memory leaks
  removeEventListeners();
  
  // Save state before cleanup
  saveState();
  
  isInitialized = false;
  console.log('✅ Pomodoro App cleanup complete');
}

// ============================================================================
// STATE SYNCHRONIZATION
// ============================================================================

// Sync state when returning to Pomodoro page
function syncBackgroundState() {
  console.log('🔄 Syncing background state...');
  
  // Load the latest state from localStorage
  const savedState = localStorage.getItem('pomodoroState');
  if (savedState) {
    try {
      const parsedState = JSON.parse(savedState);
      
      // If timer was running, calculate elapsed time
      if (parsedState.isRunning && parsedState.timeLeft > 0) {
        const now = Date.now();
        const lastSaved = parsedState.lastTick || now;
        const elapsed = Math.floor((now - lastSaved) / 1000);
        
        if (elapsed > 0) {
          parsedState.timeLeft = Math.max(0, parsedState.timeLeft - elapsed);
          parsedState.lastTick = now;
          
          console.log(`⏰ Synced timer: ${elapsed}s elapsed, ${parsedState.timeLeft}s remaining`);
          
          // Check if timer completed while away
          if (parsedState.timeLeft === 0) {
            console.log('🔔 Timer completed while away!');
            timerComplete().catch(error => {
              console.error('Error completing timer during sync:', error);
            });
            return;
          }
          
          // Update state
          Object.assign(pomodoroState, parsedState);
          saveState();
        }
      }
      
      // Update UI with current state
      updateAll();
      
      // If timer is running, restart local interval
      if (pomodoroState.isRunning) {
        startLocalInterval();
        console.log('▶️ Restarted UI updates for running timer');
      }
      
    } catch (e) {
      console.error('Error syncing background state:', e);
    }
  }
}

// ============================================================================
// SPA INTEGRATION
// ============================================================================

// Initialize Pomodoro app
window.onLoadPomodoro = function() {
  console.log('🔄 Loading Pomodoro page...');
  
  // Always cleanup previous instance first
  if (isInitialized) {
    console.log('🧹 Cleaning up previous Pomodoro instance...');
    cleanup();
  }
  
  // Reset initialization flag
  isInitialized = false;
  
  // Initialize after a short delay to ensure DOM is ready
  setTimeout(() => {
    console.log('🚀 Starting fresh Pomodoro initialization...');
    initialize();
    
    // Sync state if timer was running in background
    syncBackgroundState();
    
    window.pomodoroInitialized = true;
    window.dispatchEvent(new CustomEvent('pomodoroReady'));
  }, 100);
};

// Cleanup when leaving Pomodoro page
window.onUnloadPomodoro = function() {
  console.log('👋 Unloading Pomodoro page...');
  
  if (isInitialized) {
    // Don't stop timer - let it continue running in background
    console.log('💾 Saving timer state before page change...');
    saveState();
    
    // Only cleanup UI and event listeners, keep timer running
    cleanup();
  }
  
  window.pomodoroInitialized = false;
};

// Page visibility API - pause UI updates when hidden
document.addEventListener('visibilitychange', function() {
  if (document.hidden) {
    console.log('⏸️ Page hidden, timer continues running in background...');
    // Timer continues running, just pause UI updates
  } else {
    console.log('▶️ Page visible, resuming timer updates...');
    // Resume UI updates when page becomes visible
    if (isInitialized && pomodoroState.isRunning) {
      console.log('🔄 Resuming UI updates for running timer...');
      updateAll();
      // Restart local interval for UI updates
      startLocalInterval();
    }
  }
});

// Test function for mode switching
window.testModeSwitching = function() {
  console.log('🧪 Testing mode switching...');
  
  const modes = ['pomodoro', 'shortBreak', 'longBreak'];
  let currentIndex = 0;
  
  const testNext = () => {
    if (currentIndex < modes.length) {
      const mode = modes[currentIndex];
      console.log('🧪 Testing switch to', mode);
      switchMode(mode);
      currentIndex++;
      setTimeout(testNext, 1000);
    } else {
      console.log('🧪 Mode switching test completed');
    }
  };
  
  testNext();
};

// Test function to check mode tab elements
window.testModeTabs = function() {
  console.log('🧪 Testing mode tab elements...');
  
  const tabSelectors = [
    { id: 'pomodoroTab', dataMode: 'pomodoro', name: 'Pomodoro' },
    { id: 'shortBreakTab', dataMode: 'short', name: 'Short Break' },
    { id: 'longBreakTab', dataMode: 'long', name: 'Long Break' }
  ];
  
  tabSelectors.forEach(({ id, dataMode, name }) => {
    let element = document.getElementById(id);
    if (!element) {
      element = document.querySelector(`[data-mode="${dataMode}"]`);
    }
    
    if (element) {
      console.log(`✅ ${name} tab found:`, element.textContent);
      
      // Test clicking
      console.log(`🧪 Testing click on ${name} tab...`);
      element.click();
    } else {
      console.log(`❌ ${name} tab not found (tried ${id} and [data-mode="${dataMode}"])`);
    }
  });
};

// Make functions globally available
window.startTimer = startTimer;
window.resetTimer = resetTimer;
window.skipTimer = skipTimer;
window.switchMode = switchMode;
window.addTask = addTask;
window.toggleTask = toggleTask;
window.removeTask = removeTask;
window.showSettings = showSettings;
window.saveSettings = saveSettings;
window.showStats = showStats;
window.resetStats = resetStats;

console.log('📦 Pomodoro Timer System Loaded'); 