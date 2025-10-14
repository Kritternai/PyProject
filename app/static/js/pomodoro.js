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
  completedPomodoros: 0,
  currentSessionId: null,
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
    todayPomodoros: 0,
    todayFocusTime: 0,
    todayTasks: 0,
    todayBreaks: 0,
    lastDate: new Date().toDateString()
  }
};

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

// Reset timer for current mode
function resetTimer() {
  pomodoroState.timeLeft = getModeTime();
  pomodoroState.totalTime = getModeTime();
  pomodoroState.isRunning = false;
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
function startTimer() {
  console.log('🎯 startTimer called, current state:', {
    isRunning: pomodoroState.isRunning,
    timeLeft: pomodoroState.timeLeft
  });
  
  if (pomodoroState.isRunning) {
    console.log('⏸️ Timer is running, calling pauseTimer()');
    pauseTimer();
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

async function switchMode(mode, reset = false, isSkip = false) {
  // End current session if switching from Pomodoro mode
  if (state.mode === 'pomodoro' && state.currentSessionId) {
    try {
      await PomodoroAPI.endSession(state.currentSessionId, {
        status: 'interrupted',
        is_interrupted: true,
        actual_duration: Math.floor((state.totalTime - state.timeLeft) / 60),
        interruption_count: 1
      });
      state.currentSessionId = null;
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  }

  if (isSkip) {
    if (state.mode === 'pomodoro') {
      state.completedPomodoros++;
      // ตรวจสอบว่าควรเป็นพักยาวหรือไม่
      if (state.completedPomodoros % state.settings.longBreakInterval === 0) {
        mode = 'long';
      } else {
        mode = 'short';
      }
      state.cycle++;
    }
  } else if (reset) {
    // รีเซ็ตเมื่อมีการร้องขอ
    state.cycle = 1;
    state.completedPomodoros = 0;
  }
  
  state.mode = mode;
  state.isRunning = false;
  clearInterval(interval);
  const times = {
    pomodoro: state.settings.pomodoro * 60,
    short: state.settings.shortBreak * 60,
    long: state.settings.longBreak * 60
  };
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
function resetTimer() {
  console.log('🔄 Resetting Pomodoro timer...');
  console.log('🔄 Current mode:', pomodoroState.mode);
  
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
function skipTimer() {
  console.log('⏭️ Skipping current session...');
  console.log('⏭️ Current mode:', pomodoroState.mode);
  
  // Stop current timer
  pomodoroState.isRunning = false;
  stopAllTimers();
  
  // Complete current session if it's a pomodoro
  if (pomodoroState.mode === 'pomodoro') {
    console.log('⏭️ Completing pomodoro session...');
    completeSession();
  }
  
  // Move to next mode
  nextMode();
  
  console.log('⏭️ Switched to mode:', pomodoroState.mode);
  
  updateButtons(); // Update button state
  updateAll(); // Update all UI elements
  saveState();
}

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
// Start local interval for UI updates
function startLocalInterval() {
  if (interval) {
    clearInterval(interval);
  }

  // Reset cycle when starting a new Pomodoro session
  if (!state.isRunning && state.mode === 'pomodoro' && state.timeLeft === state.totalTime) {
    state.cycle = 1;
    state.completedPomodoros = 0;
  }
  
  state.isRunning = true;
  lastTick = Date.now();
  
  // Create new session for any mode (focus or break)
  if (!state.currentSessionId) {
    try {
      // Map frontend mode to backend session_type
      const sessionType = state.mode === 'pomodoro' ? 'focus' : 
                         state.mode === 'short' ? 'short_break' : 'long_break';
                         
      console.log('Creating session with type:', sessionType);
      
      const response = await PomodoroAPI.createSession({
        session_type: sessionType,
        duration: Math.floor(state.totalTime / 60), // Convert seconds to minutes
        task: state.currentTask ? state.currentTask.text : null,
        // Add additional data
        mood_before: getMoodState(), // เพิ่มฟังก์ชันใหม่
        energy_level: getEnergyLevel(), // เพิ่มฟังก์ชันใหม่
        auto_start_next: state.settings.autoStartBreaks,
        notification_enabled: true,
        sound_enabled: state.settings.soundEnabled
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
    if (pomodoroState.isRunning) {
      updateDisplay();
      updateButtons();
      updateModeTabs();
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
          
          // Update UI immediately
          updateDisplay();
          updateButtons();
          
          if (pomodoroState.timeLeft === 0) {
            timerComplete();
          }
        }
      }
    }
  }, 1000);
}

async function timerComplete() {
  state.isRunning = false;
  clearInterval(interval);
  
  if (state.mode === 'pomodoro') {
    // End current Pomodoro session if exists
    if (state.currentSessionId) {
      try {
        // Get session feedback from user before ending
        const feedback = getSessionFeedback();
        
        const response = await PomodoroAPI.endSession(state.currentSessionId, {
          status: 'completed',
          is_completed: true,
          actual_duration: state.settings.pomodoro,
          ...feedback // Include all feedback data
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
// Timer completed
function timerComplete() {
  console.log('🔔 Timer completed!');
  pomodoroState.isRunning = false;
  completeSession();
  
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
    
    const nextMode = state.completedPomodoros % state.settings.longBreakInterval === 0 ? 'long' : 'short';
    switchMode(nextMode);
    
    // สร้าง session ใหม่สำหรับช่วงพัก
    try {
      const sessionType = nextMode === 'short' ? 'short_break' : 'long_break';
      console.log('Creating break session:', sessionType);
      
      const response = await PomodoroAPI.createSession({
        session_type: sessionType,
        duration: nextMode === 'short' ? state.settings.shortBreak : state.settings.longBreak,
        auto_start_next: state.settings.autoStartBreaks,
        notification_enabled: true,
        sound_enabled: state.settings.soundEnabled
      });
      
      if (response.success) {
        state.currentSessionId = response.session.id;
        console.log('Created new break session:', response.session);
        
        if (state.settings.autoStartBreaks) {
          startTimer();
        }
      }
    } catch (error) {
      console.error('Failed to create break session:', error);
      showNotification('⚠️ เกิดข้อผิดพลาดในการสร้าง session พัก');
    }
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
  const modeDisplay = document.getElementById('modeDisplay');
  if (!modeDisplay) {
    console.warn('⚠️ modeDisplay element not found');
    return;
  }
  
  const modeText = {
    'pomodoro': 'Focus Time',
    'shortBreak': 'Short Break',
    'longBreak': 'Long Break'
  };
  
  const newText = modeText[pomodoroState.mode] || 'Focus Time';
  console.log('🔄 Updating mode display to:', newText, '(mode:', pomodoroState.mode, ')');
  modeDisplay.textContent = newText;
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
  if (!taskList) return;
  
  taskList.innerHTML = '';
  pomodoroState.tasks.forEach((task, index) => {
    const taskElement = document.createElement('li');
    taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;
    taskElement.innerHTML = `
      <input type="checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask(${index})">
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
      <button class="btn btn-sm btn-outline-danger" onclick="removeTask(${index})">×</button>
    `;
    taskList.appendChild(taskElement);
  });
  
  // Update task count
  const taskCount = document.getElementById('taskCount');
  if (taskCount) {
    taskCount.textContent = `${pomodoroState.tasks.length} tasks`;
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
function addTask() {
  const taskInput = document.getElementById('taskInput');
  if (!taskInput) return;
  
  const text = taskInput.value.trim();
  if (!text) return;
  
  pomodoroState.tasks.push({
    text: text,
    completed: false,
    createdAt: new Date().toISOString()
  });
  
  taskInput.value = '';
  updateTaskList();
  pomodoroState.stats.totalTasks++;
  pomodoroState.stats.todayTasks++;
  saveState();
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
// Toggle task completion
function toggleTask(index) {
  if (index >= 0 && index < pomodoroState.tasks.length) {
    pomodoroState.tasks[index].completed = !pomodoroState.tasks[index].completed;
    updateTaskList();
    saveState();
  }
}

// Remove task
function removeTask(index) {
  if (index >= 0 && index < pomodoroState.tasks.length) {
    pomodoroState.tasks.splice(index, 1);
    updateTaskList();
    saveState();
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
function saveSettings() {
  const settings = {
    pomodoro: parseInt(document.getElementById('pomodoroTime').value) || 25,
    shortBreak: parseInt(document.getElementById('shortBreakTime').value) || 5,
    longBreak: parseInt(document.getElementById('longBreakTime').value) || 15,
    longBreakInterval: parseInt(document.getElementById('longBreakInterval').value) || 4,
    autoStartBreaks: document.getElementById('autoStartBreaks').checked,
    soundEnabled: document.getElementById('soundEnabled').checked
  };
  
  pomodoroState.settings = settings;
  resetTimer();
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
    
    console.log('✅ Mode switched to', mode, 'with', pomodoroState.timeLeft, 'seconds');
    console.log('✅ Timer display should show:', Math.floor(pomodoroState.timeLeft / 60) + ':' + (pomodoroState.timeLeft % 60).toString().padStart(2, '0'));
    
    updateAll();
    saveState();
    
    console.log('✅ Mode switch completed');
  } else {
    console.log('⚠️ Already in', mode, 'mode, no change needed');
  }
}

// ---------- Session Feedback ----------
function getMoodState() {
  // สามารถเพิ่ม UI ให้ผู้ใช้เลือกอารมณ์ได้
  // ตัวอย่างค่าที่เป็นไปได้: 'energetic', 'focused', 'tired', 'distracted'
  return document.querySelector('input[name="mood"]:checked')?.value || 'neutral';
}

function getEnergyLevel() {
  // สามารถเพิ่ม UI ให้ผู้ใช้เลือกระดับพลังงานได้
  // ค่าระหว่าง 1-10
  return parseInt(document.querySelector('input[name="energy"]')?.value || '5');
}

function getSessionFeedback() {
  return {
    mood_after: getMoodState(),
    focus_score: parseInt(document.querySelector('input[name="focus"]')?.value || '5'),
    productivity_score: parseInt(document.querySelector('input[name="productivity"]')?.value || '5'),
    energy_level: getEnergyLevel(),
    difficulty_level: parseInt(document.querySelector('input[name="difficulty"]')?.value || '5')
  };
}

// ---------- Initialize ----------
function initializeApp() {
  console.log('Initializing Pomodoro Timer...');
  
  // รีเซ็ตค่าเริ่มต้น
  state.cycle = 1;
  state.completedPomodoros = 0;

  // Load saved data
  const savedState = localStorage.getItem('pomodoroState');
  if (savedState) {
    try {
      const parsed = JSON.parse(savedState);
      
      // เช็คว่าเป็นวันใหม่หรือไม่
      const today = new Date().toDateString();
      if (parsed.stats.lastDate !== today) {
        // ถ้าเป็นวันใหม่ให้รีเซ็ตค่าต่างๆ
        parsed.stats.todayPomodoros = 0;
        parsed.stats.todayFocusTime = 0;
        parsed.stats.todayTasks = 0;
        parsed.stats.todayBreaks = 0;
        parsed.stats.lastDate = today;
        parsed.cycle = 1;  // รีเซ็ตรอบเมื่อเป็นวันใหม่
        parsed.completedPomodoros = 0;
      }

      // เช็คว่ามีการ login ใหม่หรือไม่ (session หมดอายุ)
      if (!document.cookie.includes('session_id')) {
        parsed.cycle = 1;  // รีเซ็ตรอบเมื่อ login ใหม่
        parsed.completedPomodoros = 0;
      }

      Object.assign(state, parsed);
      console.log('Loaded saved state:', state);
    } catch (e) {
      console.error('Failed to load saved state:', e);
      // กรณีมีข้อผิดพลาดให้เริ่มต้นใหม่
      state.cycle = 1;
      state.completedPomodoros = 0;
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
    'statsBtn', 'closeStats', 'resetStatsBtn'
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
    resetBtn.addEventListener('click', () => {
      console.log('Reset button clicked');
      if (confirm('ต้องการรีเซ็ตทั้งเวลาและรอบการทำงานหรือไม่?')) {
        switchMode(state.mode, true);  // ส่ง true เพื่อรีเซ็ต cycle
        showNotification('🔄 รีเซ็ตเรียบร้อย!');
      }
    });
    console.log('🔗 Adding click listener to resetBtn');
    resetBtn.addEventListener('click', resetTimer);
  } else {
    console.warn('⚠️ resetBtn not found when setting up event listeners');
  }
  
  const skipBtn = document.getElementById('skipBtn');
  if (skipBtn) {
    skipBtn.addEventListener('click', () => {
      console.log('Skip button clicked');
      if (state.mode === 'pomodoro') {
        // เมื่อกด Skip ในโหมด Pomodoro
        switchMode(state.mode, false, true);
      } else {
        // เมื่อกด Skip ในโหมดพัก
        switchMode('pomodoro');
      }
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
  
  const saveSettings = document.getElementById('saveSettings');
  if (saveSettings) {
    saveSettings.addEventListener('click', saveSettings);
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
  
  const resetStatsBtn = document.getElementById('resetStatsBtn');
  if (resetStatsBtn) {
    resetStatsBtn.addEventListener('click', () => {
      console.log('Reset stats button clicked');
      if (confirm('รีเซ็ตสถิติและรอบการทำงานทั้งหมด?')) {
        // รีเซ็ตสถิติ
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
        // รีเซ็ตรอบการทำงาน
        state.cycle = 1;
        state.completedPomodoros = 0;
        
        // อัพเดทการแสดงผล
        updateStats();
        updateDisplay();
        showNotification('🔄 รีเซ็ตข้อมูลทั้งหมดเรียบร้อย!');
        document.getElementById('settingsDialog').close();
      }
    });
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
    { id: 'modeDisplay' },
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
  
  isInitialized = true;
  console.log('✅ Pomodoro App initialized');
}

// Cleanup when leaving page
function cleanup() {
  console.log('Cleaning up Pomodoro app...');
  
  // Stop timer
  console.log('🧹 Cleaning up Pomodoro App...');
  
  // Don't stop global timer - let it continue running
  // Only stop local interval for UI updates
  if (interval) {
    clearInterval(interval);
    interval = null;
  }
  
  // Reset running state
  state.isRunning = false;
  
  // Remove all event listeners by cloning and replacing elements
  const elementsToClean = [
    'startBtn', 'resetBtn', 'skipBtn', 'settingsBtn', 
    'closeSettings', 'saveSettings', 'statsBtn', 
    'closeStats', 'closeStatsBtn', 'resetStatsBtn',
    'taskInput', 'addTaskBtn'
  ];
  
  elementsToClean.forEach(id => {
    const element = document.getElementById(id);
    if (element && element.parentNode) {
      const newElement = element.cloneNode(true);
      element.parentNode.replaceChild(newElement, element);
    }
  });
  
  // Remove mode tab listeners
  const modeTabs = document.querySelectorAll('.mode-tab');
  modeTabs.forEach(tab => {
    if (tab.parentNode) {
      const newTab = tab.cloneNode(true);
      tab.parentNode.replaceChild(newTab, tab);
    }
  });
  
  // Remove task list listeners
  const taskItems = document.querySelectorAll('.task-item');
  taskItems.forEach(item => {
    if (item.parentNode) {
      const newItem = item.cloneNode(true);
      item.parentNode.replaceChild(newItem, item);
    }
  });
  
  // Save state
  localStorage.setItem('pomodoroState', JSON.stringify(state));
  
  console.log('✅ Cleanup complete');
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
            timerComplete();
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