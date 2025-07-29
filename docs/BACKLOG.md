# Product Backlog: Smart Learning Hub (อัปเดตล่าสุด)

เอกสารนี้คือรายการของฟีเจอร์, งาน, และการปรับปรุงทั้งหมดของโปรเจกต์ (Product Backlog) โดยจะเรียงลำดับความสำคัญจากบนลงล่าง ทีมจะดึงงานจากบนสุดของรายการนี้ไปทำก่อน

---

## User Stories

### Epic: User Management
- **US-01: User Registration/Login/Google OAuth**
  - **As a** new/returning user,
  - **I want to** register/login (email, password, Google OAuth),
  - **so that** I can save and sync my learning progress.
  - **Acceptance Criteria:**
    - [ ] Unique email, hashed password, Google OAuth
    - [ ] User auto-login after registration
    - [ ] Error for incorrect credentials

### Epic: Lesson Management
- **LM-01: Create/Edit/Delete Lesson**
  - **As a** user,
  - **I want to** create, edit, delete lessons with tags/status,
  - **so that** I can organize my study materials.
  - **Acceptance Criteria:**
    - [ ] Title required, Markdown content, tag support
    - [ ] Status: Not Started, In Progress, Completed
- **LM-02: Google Classroom Integration**
  - **As a** user,
  - **I want to** import courses/assignments/files from Google Classroom,
  - **so that** I can manage all learning in one place.
  - **Acceptance Criteria:**
    - [ ] OAuth2, import/update courses, show assignments/files

### Epic: Note-Taking
- **NT-01: Create/Edit/Delete Note**
  - **As a** user,
  - **I want to** create notes with Markdown, link to lessons,
  - **so that** I can summarize and search my knowledge.
  - **Acceptance Criteria:**
    - [ ] Markdown, tag, link to lesson, search

### Epic: Chrome Extension Integration
- **EXT-01: Import Data from MS Teams/KMITL**
  - **As a** user,
  - **I want to** import schedule/assignment data from MS Teams/KMITL via Chrome Extension,
  - **so that** I can centralize my learning data.
  - **Acceptance Criteria:**
    - [ ] Extension sends data to Flask API, data mapped to lessons/tasks

### Epic: Task & To-Do (In Progress)
- **TSK-01: Create/Edit/Delete Task**
  - **As a** user,
  - **I want to** create tasks with due date, priority, reminder,
  - **so that** I can manage my assignments and deadlines.
  - **Acceptance Criteria:**
    - [ ] CRUD, due date, priority, reminder

### Epic: Pomodoro Timer (In Progress)
- **PT-01: Pomodoro Timer**
  - **As a** user,
  - **I want to** use a Pomodoro timer with custom durations,
  - **so that** I can focus and track my study sessions.
  - **Acceptance Criteria:**
    - [ ] Set work/break/long break, notification, session log

### Epic: Progress Tracking (Planned)
- **PRG-01: Dashboard & Report**
  - **As a** user,
  - **I want to** see my progress (lessons, tasks, pomodoro),
  - **so that** I can track and improve my learning.
  - **Acceptance Criteria:**
    - [ ] Dashboard, summary report, export

---

## Technical Tasks & Chores
- **TECH-01:** Set up/maintain SQLite, SQLAlchemy models
- **TECH-02:** Integrate Google API, Chrome Extension API
- **TECH-03:** Refactor for OOP/Modular, improve code quality
- **TECH-04:** Add/maintain Unit Test, Integration Test
- **TECH-05:** CI/CD, Linter (e.g., Ruff)
- **DOC-01:** Update documentation (Proposal, Roadmap, Backlog, User Guide)
