# Product Backlog: Smart Learning Hub

เอกสารนี้คือรายการของฟีเจอร์, งาน, และการปรับปรุงทั้งหมดของโปรเจกต์ (Product Backlog) โดยจะเรียงลำดับความสำคัญจากบนลงล่าง ทีมจะดึงงานจากบนสุดของรายการนี้ไปทำก่อน

---

## User Stories

### Epic: User Management

- **US-01: User Registration**
  - **As a** new user,
  - **I want to** register for an account using my email and a password,
  - **so that** I can save my learning progress.
  - **Acceptance Criteria:**
    - [ ] User must provide a unique email.
    - [ ] Password must be stored securely (hashed).
    - [ ] User is automatically logged in after successful registration.

- **US-02: User Login**
  - **As a** registered user,
  - **I want to** log in to the system,
  - **so that** I can access my personal learning hub.
  - **Acceptance Criteria:**
    - [ ] User can log in with correct email and password.
    - [ ] System shows an error for incorrect credentials.

### Epic: Lesson Management

- **LM-01: Create a Lesson**
  - **As a** user,
  - **I want to** create a new lesson with a title and content,
  - **so that** I can organize my study materials.
  - **Acceptance Criteria:**
    - [ ] A lesson must have a title.
    - [ ] Content can be written in Markdown format.

- **LM-02: View All Lessons**
  - **As a** user,
  - **I want to** see a list of all my lessons,
  - **so that** I can choose which one to study.

### Epic: Pomodoro Timer

- **PT-01: Start Pomodoro Timer**
  - **As a** user,
  - **I want to** start a Pomodoro timer with customizable work and break durations,
  - **so that** I can focus on my tasks and take regular breaks.
  - **Acceptance Criteria:**
    - [ ] User can set work duration (e.g., 25 minutes).
    - [ ] User can set short break duration (e.g., 5 minutes).
    - [ ] User can set long break duration (e.g., 15 minutes).
    - [ ] Timer counts down and notifies the user when a session ends.

- **PT-02: Track Pomodoro Sessions**
  - **As a** user,
  - **I want to** see a record of my completed Pomodoro sessions,
  - **so that** I can track my focus time.
  - **Acceptance Criteria:**
    - [ ] System records the start and end time of each Pomodoro session.
    - [ ] User can view a summary of daily/weekly Pomodoro sessions.

### Epic: Note-Taking

- **NT-01: Create a Note**
  - **As a** user,
  - **I want to** create a note with Markdown support,
  - **so that** I can jot down my thoughts and summaries.

---

## Technical Tasks & Chores

- **TECH-01:** Set up SQLite for data storage.
- **TECH-02:** Create a basic Command-Line Interface (CLI) for interaction.
- **CHORE-01:** Configure a linter (e.g., Ruff) for the project.
