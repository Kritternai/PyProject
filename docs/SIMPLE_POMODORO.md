# 🍅 Simple Pomodoro Timer

## 📋 **Overview**

Simple standalone Pomodoro timer implementation without complex OOP architecture. Just works!

## 🎯 **Features**

### **✅ Core Functionality**
- **25-minute focus sessions**
- **5-minute short breaks**
- **15-minute long breaks** (every 4 sessions)
- **Start/Pause/Resume/Reset** controls
- **Session counter** (0/4)
- **Audio notifications**
- **Visual progress indicator**

### **✅ User Interface**
- **Clean, modern design**
- **Responsive layout**
- **Bootstrap 5 styling**
- **Font Awesome icons**
- **Real-time timer display**

### **✅ Smart Features**
- **Auto-break detection**
- **Session type switching**
- **Progress tracking**
- **Notification system**

## 📁 **Files Structure**

### **Frontend:**
- `app/static/js/pomodoro.js` - Main JavaScript class
- `app/templates/pomodoro_simple.html` - HTML template

### **Backend:**
- `app/presentation/routes/pomodoro_simple.py` - Simple routes

### **Total Files: 3** (vs 10+ in OOP version)

## 🚀 **Usage**

### **1. Access Pomodoro**
- Click "Pomodoro" in the navbar
- Or go to: `http://localhost:5004/pomodoro`

### **2. Basic Controls**
- **Start**: Begin a 25-minute focus session
- **Pause**: Pause the current session
- **Resume**: Resume a paused session
- **Reset**: Stop and reset to 25:00

### **3. Quick Actions**
- **Focus (25min)**: Set to focus mode
- **Short Break (5min)**: Set to short break
- **Long Break (15min)**: Set to long break

### **4. Automatic Features**
- **Auto-break**: Automatically starts break after focus session
- **Session counter**: Tracks sessions (0/4)
- **Long break**: Every 4 sessions = 15-minute break
- **Notifications**: Audio and visual alerts

## 🎮 **How It Works**

### **Session Flow:**
1. **Start** → 25-minute focus session
2. **Complete** → Auto-start 5-minute break
3. **Repeat** → 3 more focus sessions
4. **Long Break** → 15-minute break after 4 sessions
5. **Reset** → Back to focus mode

### **Timer Logic:**
- **Focus**: 25 minutes
- **Short Break**: 5 minutes  
- **Long Break**: 15 minutes
- **Counter**: Resets every 4 sessions

## 🔧 **Technical Details**

### **JavaScript Class:**
```javascript
class SimplePomodoro {
    constructor() {
        this.isRunning = false;
        this.isPaused = false;
        this.timeLeft = 25 * 60;
        this.sessionType = 'focus';
        this.sessionCount = 0;
        // ... more properties
    }
}
```

### **Key Methods:**
- `start()` - Start timer
- `pause()` - Pause timer
- `resume()` - Resume timer
- `reset()` - Reset timer
- `completeSession()` - Handle completion
- `startBreak()` - Auto-start break

### **No Database Required:**
- Pure frontend implementation
- No backend complexity
- No API calls needed
- Works offline

## 🎉 **Benefits**

### **✅ Simple & Fast**
- **3 files** vs 10+ files in OOP version
- **No database** complexity
- **No API** calls
- **Instant** loading

### **✅ Reliable**
- **No server** dependencies
- **No database** errors
- **No API** failures
- **Always** works

### **✅ Maintainable**
- **Easy** to understand
- **Easy** to modify
- **Easy** to debug
- **Easy** to extend

## 🌐 **Access**

- **URL**: `http://localhost:5004/pomodoro`
- **Navbar**: Click "Pomodoro"
- **Direct**: Direct link access

## 🎯 **Perfect For**

- **Students** who need focus time
- **Developers** who want simple tools
- **Anyone** who needs productivity
- **Quick** implementation
- **Standalone** usage

## 🚀 **Ready to Use!**

**Just click "Pomodoro" in the navbar and start focusing!** 🍅✨
