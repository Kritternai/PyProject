// ---------- API Service ----------
const PomodoroAPI = {
  // Create new session
  async createSession(sessionData) {
      try {
          const response = await fetch('/api/pomodoro/session', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(sessionData)
          });
          return await response.json();
      } catch (error) {
          console.error('Error creating session:', error);
          throw error;
      }
  },

  // End session
  async endSession(sessionId, data) {
      try {
          const response = await fetch(`/api/pomodoro/session/${sessionId}/end`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(data)
          });
          return await response.json();
      } catch (error) {
          console.error('Error ending session:', error);
          throw error;
      }
  },

  // Update session
  async updateSession(sessionId, data) {
      try {
          const response = await fetch(`/api/pomodoro/session/${sessionId}`, {
              method: 'PUT',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(data)
          });
          return await response.json();
      } catch (error) {
          console.error('Error updating session:', error);
          throw error;
      }
  }
};

// ---------- State ----------
const state = {
  mode: 'pomodoro',
  isRunning: false,
  timeLeft: 25 * 60,
  totalTime: 25 * 60,
  cycle: 1,
  completedPomodoros: 0,
  currentSessionId: null,
  tasks: [],
  settings: {
    pomodoro: 25,
    shortBreak: 5,
    longBreak: 15,
    longBreakInterval: 4,
    autoStartBreaks: false,
    soundEnabled: true
  },
  stats: {
    todayPomodoros: 0,
    todayFocusTime: 0,
    todayTasks: 0,
    todayBreaks: 0,
    totalPomodoros: 0,
    totalFocusTime: 0,
    totalTasks: 0,
    lastDate: new Date().toDateString()
  }
};

let interval = null;

// ---------- Utils ----------
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatHours(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

function showNotification(text) {
  const notification = document.getElementById('notification');
  document.getElementById('notificationText').textContent = text;
  notification.classList.add('show');
  
  setTimeout(() => {
    notification.classList.remove('show');
  }, 3000);
}

// ---------- Core Timer Logic ----------
function updateDisplay() {
  document.getElementById('timeDisplay').textContent = formatTime(state.timeLeft);
  const progress = ((state.totalTime - state.timeLeft) / state.totalTime) * 100;
  document.getElementById('progressBar').style.width = `${progress}%`;
  
  document.getElementById('cycleInfo').textContent = `รอบที่ #${state.cycle}`;
  
  const statusTexts = {
    pomodoro: 'เวลาที่จะมุ่งมั่น!',
    short: 'พักสั้นๆ',
    long: 'พักยาว ผ่อนคลาย'
  };
  document.getElementById('statusText').textContent = statusTexts[state.mode];
  
  document.getElementById('startBtn').textContent = state.isRunning ? 'Stop' : 'Start';
  document.title = `${formatTime(state.timeLeft)} - Focus Timer`;
}

async function switchMode(mode) {
  // End current session if switching from Pomodoro mode
  if (state.mode === 'pomodoro' && state.currentSessionId) {
    try {
      await PomodoroAPI.endSession(state.currentSessionId, {
        status: 'interrupted',
        is_interrupted: true,
        actual_duration: Math.floor((state.totalTime - state.timeLeft) / 60),
        interruption_count: 1,
        interruption_reasons: 'Mode switched'
      });
      state.currentSessionId = null;
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  }
  
  state.mode = mode;
  state.isRunning = false;
  clearInterval(interval);
  const times = {
    pomodoro: state.settings.pomodoro * 60,
    short: state.settings.shortBreak * 60,
    long: state.settings.longBreak * 60
  };
  
  state.timeLeft = times[mode];
  state.totalTime = times[mode];
  
  document.querySelectorAll('.mode-tab').forEach(tab => {
    tab.classList.remove('active');
    if (tab.dataset.mode === mode) {
      tab.classList.add('active');
    }
  });
  
  document.body.className = mode === 'pomodoro' ? '' : mode === 'short' ? 'short-break' : 'long-break';
  updateDisplay();
}

let lastTick = Date.now();

async function startTimer() {
  if (state.isRunning) {
    state.isRunning = false;
    clearInterval(interval);
    updateDisplay();
    
    // If stopping a Pomodoro session, update the session
    if (state.mode === 'pomodoro' && state.currentSessionId) {
      try {
        const elapsedMinutes = Math.floor((state.totalTime - state.timeLeft) / 60);
        await PomodoroAPI.updateSession(state.currentSessionId, {
          actual_duration: elapsedMinutes,
          status: 'paused'
        });
      } catch (error) {
        console.error('Failed to update session:', error);
      }
    }
    return;
  }
  
  state.isRunning = true;
  lastTick = Date.now();
  
  // Create new session if starting a Pomodoro
  if (state.mode === 'pomodoro' && !state.currentSessionId) {
    try {
      // Map frontend mode to backend session_type
      const sessionType = state.mode === 'pomodoro' ? 'focus' : 
                         state.mode === 'short' ? 'short_break' : 'long_break';
                         
      console.log('Creating session with type:', sessionType);
      
      const response = await PomodoroAPI.createSession({
        session_type: sessionType,
        duration: Math.floor(state.totalTime / 60), // Convert seconds to minutes
        task: state.currentTask ? state.currentTask.text : null
      });
      
      if (response.success) {
        state.currentSessionId = response.session.id;
        console.log('Created new session:', response.session);
      } else {
        console.error('Failed to create session - response:', response);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
      showNotification('⚠️ เกิดข้อผิดพลาดในการสร้าง session');
    }
  }
  
  updateDisplay();
  
  interval = setInterval(() => {
    const now = Date.now();
    const delta = Math.floor((now - lastTick) / 1000);
    
    if (delta >= 1) {
      if (state.timeLeft > 0) {
        state.timeLeft = Math.max(0, state.timeLeft - delta);
        lastTick = now;
        updateDisplay();
        
        if (state.timeLeft === 0) {
          timerComplete();
        }
      }
    }
  }, 100); // Run every 100ms for more accurate timing
}

async function timerComplete() {
  state.isRunning = false;
  clearInterval(interval);
  
  if (state.mode === 'pomodoro') {
    // End current Pomodoro session if exists
    if (state.currentSessionId) {
      try {
        const response = await PomodoroAPI.endSession(state.currentSessionId, {
          status: 'completed',
          is_completed: true,
          actual_duration: state.settings.pomodoro,
          productivity_score: 10 // สามารถปรับตามความเหมาะสม
        });
        state.currentSessionId = null;
      } catch (error) {
        console.error('Failed to end session:', error);
      }
    }
    
    state.completedPomodoros++;
    state.stats.todayPomodoros++;
    state.stats.totalPomodoros++;
    state.stats.todayFocusTime += state.settings.pomodoro;
    state.stats.totalFocusTime += state.settings.pomodoro;
    
    showNotification('🎉 Pomodoro สำเร็จ!');
    
    if (state.completedPomodoros % state.settings.longBreakInterval === 0) {
      switchMode('long');
    } else {
      switchMode('short');
    }
    
    if (state.settings.autoStartBreaks) {
      startTimer();
    }
  } else {
    state.cycle++;
    state.stats.todayBreaks++;
    showNotification('✨ พักเสร็จแล้ว!');
    switchMode('pomodoro');
    
    if (state.settings.autoStartBreaks) {
      startTimer();
    }
  }
  
  updateStats();
  playSound();
}

// ---------- Task Management ----------
function updateTaskList() {
  const list = document.getElementById('taskList');
  list.innerHTML = '';
  
  state.tasks.forEach(task => {
    const li = document.createElement('li');
    li.className = `task-item${task.completed ? ' completed' : ''}`;
    li.dataset.id = task.id;
    
    li.innerHTML = `
      <input type="checkbox" class="checkbox" ${task.completed ? 'checked' : ''}>
      <span class="task-text">${task.text}</span>
      <span class="task-pomodoros">${task.pomodoros} 🍅</span>
      <button class="select-btn" ${task.completed ? 'disabled' : ''}>เลือก</button>
      <button class="delete-btn">×</button>
    `;
    
    li.querySelector('.checkbox').addEventListener('change', () => {
      toggleTask(task.id);
    });
    
    li.querySelector('.delete-btn').addEventListener('click', () => {
      deleteTask(task.id);
    });

    li.querySelector('.select-btn').addEventListener('click', () => {
      selectCurrentTask(task.id);
    });
    
    list.appendChild(li);
  });
  
  document.getElementById('taskCount').textContent = `${state.tasks.length} งาน`;
}

function addTask(text) {
  if (!text.trim()) return;
  
  const task = {
    id: Date.now(),
    text: text.trim(),
    completed: false,
    pomodoros: 0
  };
  
  state.tasks.unshift(task);
  updateTaskList();
  document.getElementById('taskInput').value = '';
}

function toggleTask(id) {
  const task = state.tasks.find(t => t.id === id);
  if (task) {
    task.completed = !task.completed;
    if (task.completed) {
      state.stats.todayTasks++;
      state.stats.totalTasks++;
      updateStats();
    } else {
      // เมื่อ uncheck task ให้กำหนดเป็น current task
      state.currentTask = task;
    }
    updateTaskList();
    updateCurrentTaskDisplay();
  }
}

function deleteTask(id) {
  state.tasks = state.tasks.filter(t => t.id !== id);
  if (state.currentTask && state.currentTask.id === id) {
    state.currentTask = null;
  }
  updateTaskList();
  updateCurrentTaskDisplay();
}

function selectCurrentTask(id) {
  const task = state.tasks.find(t => t.id === id);
  if (task && !task.completed) {
    state.currentTask = task;
    updateCurrentTaskDisplay();
  }
}

function updateCurrentTaskDisplay() {
  const currentTaskDisplay = document.getElementById('currentTaskDisplay');
  if (currentTaskDisplay) {
    currentTaskDisplay.textContent = state.currentTask 
      ? `กำลังทำ: ${state.currentTask.text}` 
      : 'ไม่ได้เลือกงาน';
  }
}

// ---------- Stats & Settings ----------
function updateStats() {
  document.getElementById('completedPomodoros').textContent = state.stats.todayPomodoros;
  document.getElementById('focusTime').textContent = formatHours(state.stats.todayFocusTime);
  document.getElementById('completedTasks').textContent = state.stats.todayTasks;
  document.getElementById('totalBreaks').textContent = state.stats.todayBreaks;
  
  document.getElementById('totalPomodoros').textContent = state.stats.totalPomodoros;
  document.getElementById('totalFocusTime').textContent = formatHours(state.stats.totalFocusTime);
  document.getElementById('totalTasksCompleted').textContent = state.stats.totalTasks;
}

function openSettings() {
  const dialog = document.getElementById('settingsDialog');
  
  document.getElementById('pomodoroTime').value = state.settings.pomodoro;
  document.getElementById('shortBreakTime').value = state.settings.shortBreak;
  document.getElementById('longBreakTime').value = state.settings.longBreak;
  document.getElementById('longBreakInterval').value = state.settings.longBreakInterval;
  document.getElementById('autoStartBreaks').checked = state.settings.autoStartBreaks;
  document.getElementById('soundEnabled').checked = state.settings.soundEnabled;
  
  dialog.showModal();
}

function saveSettings() {
  state.settings = {
    pomodoro: parseInt(document.getElementById('pomodoroTime').value) || 25,
    shortBreak: parseInt(document.getElementById('shortBreakTime').value) || 5,
    longBreak: parseInt(document.getElementById('longBreakTime').value) || 15,
    longBreakInterval: parseInt(document.getElementById('longBreakInterval').value) || 4,
    autoStartBreaks: document.getElementById('autoStartBreaks').checked,
    soundEnabled: document.getElementById('soundEnabled').checked
  };
  
  document.getElementById('settingsDialog').close();
  switchMode(state.mode);
}

// ---------- Sound Effects ----------
function playSound() {
  if (!state.settings.soundEnabled) return;
  
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  } catch (e) {
    console.error('Sound playback failed:', e);
  }
}

// ---------- Initialize ----------
function initializeApp() {
  console.log('Initializing Pomodoro Timer...');

  // Load saved data
  const savedState = localStorage.getItem('pomodoroState');
  if (savedState) {
    try {
      const parsed = JSON.parse(savedState);
      Object.assign(state, parsed);
      console.log('Loaded saved state:', state);
    } catch (e) {
      console.error('Failed to load saved state:', e);
    }
  }

  // Check if it's a new day
  const today = new Date().toDateString();
  if (state.stats.lastDate !== today) {
    console.log('New day detected, resetting daily stats');
    state.stats.todayPomodoros = 0;
    state.stats.todayFocusTime = 0;
    state.stats.todayTasks = 0;
    state.stats.todayBreaks = 0;
    state.stats.lastDate = today;
  }

  // Initialize displays
  console.log('Initializing displays...');
  updateDisplay();
  updateStats();
  updateTaskList();

  // Timer Controls
  console.log('Setting up timer controls...');
  const startBtn = document.getElementById('startBtn');
  const resetBtn = document.getElementById('resetBtn');
  const skipBtn = document.getElementById('skipBtn');

  if (startBtn) {
    startBtn.addEventListener('click', () => {
      console.log('Start/Pause button clicked');
      startTimer();
    });
  } else {
    console.error('Start button not found!');
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      console.log('Reset button clicked');
      switchMode(state.mode);
    });
  } else {
    console.error('Reset button not found!');
  }

  if (skipBtn) {
    skipBtn.addEventListener('click', () => {
      console.log('Skip button clicked');
      timerComplete();
    });
  } else {
    console.error('Skip button not found!');
  }

  // Mode Tabs
  console.log('Setting up mode tabs...');
  const modeTabs = document.querySelectorAll('.mode-tab');
  modeTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      console.log('Mode changed to:', tab.dataset.mode);
      switchMode(tab.dataset.mode);
    });
  });

  // Task Management
  console.log('Setting up task management...');
  const taskInput = document.getElementById('taskInput');
  const addTaskBtn = document.getElementById('addTaskBtn');

  if (taskInput) {
    taskInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        console.log('Adding task via Enter key');
        addTask(e.target.value);
      }
    });
  }

  if (addTaskBtn) {
    addTaskBtn.addEventListener('click', () => {
      console.log('Adding task via button click');
      const input = document.getElementById('taskInput');
      if (input) {
        addTask(input.value);
      }
    });
  }

  // Settings Dialog
  console.log('Setting up settings dialog...');
  const settingsBtn = document.getElementById('settingsBtn');
  const closeSettings = document.getElementById('closeSettings');
  const saveSettingsBtn = document.getElementById('saveSettings');
  const settingsDialog = document.getElementById('settingsDialog');

  if (settingsBtn && settingsDialog) {
    settingsBtn.addEventListener('click', () => {
      console.log('Opening settings dialog');
      openSettings();
    });
  }

  if (closeSettings) {
    closeSettings.addEventListener('click', () => {
      console.log('Closing settings dialog');
      settingsDialog.close();
    });
  }

  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener('click', () => {
      console.log('Saving settings');
      // call the settings save function defined above
      saveSettings();
    });
  }

  // Stats Dialog
  console.log('Setting up stats dialog...');
  const statsBtn = document.getElementById('statsBtn');
  const closeStats = document.getElementById('closeStats');
  const closeStatsBtn = document.getElementById('closeStatsBtn');
  const statsDialog = document.getElementById('statsDialog');

  if (statsBtn && statsDialog) {
    statsBtn.addEventListener('click', () => {
      console.log('Opening stats dialog');
      statsDialog.showModal();
    });
  }

  if (closeStats) {
    closeStats.addEventListener('click', () => {
      console.log('Closing stats dialog');
      statsDialog.close();
    });
  }

  if (closeStatsBtn) {
    closeStatsBtn.addEventListener('click', () => {
      console.log('Closing stats dialog via button');
      statsDialog.close();
    });
  }

  // Reset Stats
  console.log('Setting up stats reset...');
  const resetStatsBtn = document.getElementById('resetStatsBtn');
  if (resetStatsBtn) {
    resetStatsBtn.addEventListener('click', () => {
      console.log('Reset stats button clicked');
      if (confirm('รีเซ็ตสถิติทั้งหมด?')) {
        state.stats = {
          todayPomodoros: 0,
          todayFocusTime: 0,
          todayTasks: 0,
          todayBreaks: 0,
          totalPomodoros: 0,
          totalFocusTime: 0,
          totalTasks: 0,
          lastDate: new Date().toDateString()
        };
        updateStats();
      }
    });
  }

  // Keyboard Shortcuts
  console.log('Setting up keyboard shortcuts...');
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return;
    
    if (e.code === 'Space') {
      e.preventDefault();
      console.log('Space pressed - Start/Pause timer');
      startTimer();
    } else if (e.key.toLowerCase() === 'r') {
      console.log('R pressed - Reset timer');
      switchMode(state.mode);
    }
  });

  // Auto-save state
  console.log('Setting up auto-save...');
  setInterval(() => {
    // Save only if state has changed
    const currentState = JSON.stringify(state);
    if (currentState !== localStorage.getItem('pomodoroState')) {
      localStorage.setItem('pomodoroState', currentState);
      console.log('State auto-saved');
    }
  }, 10000); // Save every 10 seconds instead

  console.log('Initialization complete!');
}

// Cleanup function to stop timer and save state
function cleanup() {
  console.log('Cleaning up Pomodoro app...');
  if (interval) {
    clearInterval(interval);
    interval = null;
  }
  state.isRunning = false;
  localStorage.setItem('pomodoroState', JSON.stringify(state));
}

// Flag to track initialization status
let isInitialized = false;

// Make functions globally available for SPA
window.onLoadPomodoro = function() {
  console.log('🔄 onLoadPomodoro called');
  
  // If already initialized, cleanup first
  if (isInitialized) {
    console.log('🧹 Cleaning up previous instance...');
    cleanup();
  }
  
  console.log('🚀 Initializing Pomodoro app...');
  initializeApp();
  isInitialized = true;
  console.log('✅ Initialization complete');
  
  // Notify main.js that initialization is complete
  window.pomodoroInitialized = true;
  
  // Dispatch custom event
  window.dispatchEvent(new CustomEvent('pomodoroReady'));
}

window.onUnloadPomodoro = function() {
  console.log('👋 Unloading Pomodoro app...');
  cleanup();
  isInitialized = false;
  window.pomodoroInitialized = false;
}

// Initialize on script load
console.log('📥 pomodoro.js loaded');
window.pomodoroLoaded = true;

// Also initialize on direct page load if not in SPA mode
if (!window.isInSpaMode) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.onLoadPomodoro);
  } else {
    window.onLoadPomodoro();
  }
}
