// Pomodoro Timer Logic
let timer;
let timeLeft = 25 * 60;
let mode = 'pomodoro';
let isRunning = false;
let completed = 0;

const display = document.getElementById('timer-display');
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const resetBtn = document.getElementById('reset-btn');
const modeBtns = document.querySelectorAll('.mode-btn');
const progressBar = document.getElementById('progress-bar');
const completedSessions = document.getElementById('completed-sessions');

function updateDisplay() {
  const min = String(Math.floor(timeLeft / 60)).padStart(2, '0');
  const sec = String(timeLeft % 60).padStart(2, '0');
  display.textContent = `${min}:${sec}`;
  let percent = 0;
  if (mode === 'pomodoro') percent = 100 - (timeLeft / (25 * 60)) * 100;
  if (mode === 'short') percent = 100 - (timeLeft / (5 * 60)) * 100;
  if (mode === 'long') percent = 100 - (timeLeft / (15 * 60)) * 100;
  progressBar.style.width = percent + '%';
}

function startTimer() {
  if (isRunning) return;
  isRunning = true;
  timer = setInterval(() => {
    if (timeLeft > 0) {
      timeLeft--;
      updateDisplay();
    } else {
      clearInterval(timer);
      isRunning = false;
      completed++;
      completedSessions.textContent = completed;
      alert('Time is up!');
    }
  }, 1000);
}

function pauseTimer() {
  clearInterval(timer);
  isRunning = false;
}

function resetTimer() {
  pauseTimer();
  if (mode === 'pomodoro') timeLeft = 25 * 60;
  if (mode === 'short') timeLeft = 5 * 60;
  if (mode === 'long') timeLeft = 15 * 60;
  updateDisplay();
}

modeBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    modeBtns.forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    mode = this.dataset.mode;
    resetTimer();
  });
});

startBtn.addEventListener('click', startTimer);
pauseBtn.addEventListener('click', pauseTimer);
resetBtn.addEventListener('click', resetTimer);

updateDisplay();
