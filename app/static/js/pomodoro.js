// ---------- State ----------
const state = {
  mode: 'pomodoro',
  isRunning: false,
  timeLeft: 25 * 60,
  totalTime: 25 * 60,
  cycle: 1,
  completedPomodoros: 0,
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
  
  document.getElementById('startBtn').textContent = state.isRunning ? 'หยุด' : 'เริ่ม';
  document.title = `${formatTime(state.timeLeft)} - Focus Timer`;
}

function switchMode(mode) {
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

function startTimer() {
  if (state.isRunning) {
    state.isRunning = false;
    clearInterval(interval);
    updateDisplay();
    return;
  }
  
  state.isRunning = true;
  updateDisplay();
  
  interval = setInterval(() => {
    if (state.timeLeft > 0) {
      state.timeLeft--;
      updateDisplay();
    } else {
      timerComplete();
    }
  }, 1000);
}

function timerComplete() {
  state.isRunning = false;
  clearInterval(interval);
  
  if (state.mode === 'pomodoro') {
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
      <button class="delete-btn">×</button>
    `;
    
    li.querySelector('.checkbox').addEventListener('change', () => {
      toggleTask(task.id);
    });
    
    li.querySelector('.delete-btn').addEventListener('click', () => {
      deleteTask(task.id);
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
    }
    updateTaskList();
  }
}

function deleteTask(id) {
  state.tasks = state.tasks.filter(t => t.id !== id);
  updateTaskList();
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
document.addEventListener('DOMContentLoaded', () => {
  // Load saved data
  const savedState = localStorage.getItem('pomodoroState');
  if (savedState) {
    try {
      Object.assign(state, JSON.parse(savedState));
    } catch (e) {
      console.error('Failed to load saved state:', e);
    }
  }

  // Check if it's a new day
  const today = new Date().toDateString();
  if (state.stats.lastDate !== today) {
    state.stats.todayPomodoros = 0;
    state.stats.todayFocusTime = 0;
    state.stats.todayTasks = 0;
    state.stats.todayBreaks = 0;
    state.stats.lastDate = today;
  }

  // Initialize display
  updateDisplay();
  updateStats();
  updateTaskList();

  // Timer Controls
  document.getElementById('startBtn').addEventListener('click', startTimer);
  document.getElementById('resetBtn').addEventListener('click', () => switchMode(state.mode));
  document.getElementById('skipBtn').addEventListener('click', timerComplete);

  // Mode Tabs
  document.querySelectorAll('.mode-tab').forEach(tab => {
    tab.addEventListener('click', () => switchMode(tab.dataset.mode));
  });

  // Task Input
  document.getElementById('taskInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      addTask(e.target.value);
    }
  });
  document.getElementById('addTaskBtn').addEventListener('click', () => {
    addTask(document.getElementById('taskInput').value);
  });

  // Settings Dialog
  document.getElementById('settingsBtn').addEventListener('click', openSettings);
  document.getElementById('closeSettings').addEventListener('click', () => {
    document.getElementById('settingsDialog').close();
  });
  document.getElementById('saveSettings').addEventListener('click', saveSettings);

  // Stats Dialog
  document.getElementById('statsBtn').addEventListener('click', () => {
    document.getElementById('statsDialog').showModal();
  });
  document.getElementById('closeStats').addEventListener('click', () => {
    document.getElementById('statsDialog').close();
  });
  document.getElementById('closeStatsBtn').addEventListener('click', () => {
    document.getElementById('statsDialog').close();
  });

  // Reset Stats
  document.getElementById('resetStatsBtn').addEventListener('click', () => {
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

  // Keyboard Shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return;
    
    if (e.code === 'Space') {
      e.preventDefault();
      startTimer();
    } else if (e.key.toLowerCase() === 'r') {
      switchMode(state.mode);
    }
  });

  // Save state periodically
  setInterval(() => {
    localStorage.setItem('pomodoroState', JSON.stringify(state));
  }, 1000);
});
