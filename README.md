# Orario - AI-Powered Student Productivity Platform
<img width="1156" height="338" alt="Screenshot 2026-07-21 at 7 18 17 am" src="https://github.com/user-attachments/assets/7030ddaf-d719-4eb6-a9f1-e051bf976279" />
Orario comes from the Greek word 'ωράριο' meaning timetable or scheduling.

Orario is a full-stack web application designed to help students organise their studies through task management, AI-generated flashcards, Pomodoro study sessions, collaborative study groups and productivity analytics. The application combines modern web technologies with secure authentication and user-centred design to provide an integrated study platform.

## Core Features

### Security & Architecture
- **Secure Authentication:** Robust registration and login system with secure session management and password hashing using `werkzeug.security`.
- **Built-in Security:** Implements CSRF protection, server-side input validation and input sanitisation to help protect against common web application attacks.
- **Persistent User Preferences:** User settings, including personalised dashboard quotes, are stored in the database and synchronised across devices.
- **Responsive Design:** Fully responsive interface optimised for desktop, tablet and mobile devices.
<img width="619" height="731" alt="Screenshot 2026-07-21 at 7 22 25 am" src="https://github.com/user-attachments/assets/d200719b-ea09-42e9-92ab-09c844da1afd" />

### Task Management & Interactive Calendar
- **Complete Task Management:** Create, edit and delete tasks with optional reminder notifications.
<img width="1204" height="506" alt="Screenshot 2026-07-21 at 7 21 06 am" src="https://github.com/user-attachments/assets/5a0da689-07c8-4fc6-b22d-b3a482fc3584" />
- **Interactive Calendar:** View colour-coded task status directly within the calendar (red for incomplete tasks and green for completed tasks)
- **Task Preview:** Hover over calendar dates to display a preview of scheduled tasks.
<img width="1138" height="603" alt="Screenshot 2026-07-21 at 7 20 11 am" src="https://github.com/user-attachments/assets/c18e239e-9538-4855-a3d4-6401e518729b" />

### AI Flashcard Generator
- **AI-Powered Flashcards:** Generate a specified number of flashcards from uploaded study materials or custom prompts.
- **Reliable Generation:** AI responses are validated automatically, with retry logic used to recover from malformed outputs and improve reliability.
<img width="1463" height="815" alt="Screenshot 2026-07-21 at 7 23 01 am" src="https://github.com/user-attachments/assets/2799d25c-0c72-4cee-a6aa-493c20cfc1b4" />

### Pomodoro Timer & Study Tools
- **Persistent Timer:** Includes configurable work, short break and long break sessions. Timer progress is automatically restored after page refreshes or browser navigation.
- **Custom Study Sessions:** Adjust Pomodoro intervals to suit individual study preferences.
- **Integrated Music Player:** Built-in Spotify LoFi playlist to provide background music during study sessions.
<img width="1465" height="812" alt="Screenshot 2026-07-21 at 7 23 58 am" src="https://github.com/user-attachments/assets/2b977841-29a8-4824-b8ae-d5d3c6fd5139" />

### Study Groups & Analytics
- **Study Groups:** Join collaborative study groups and compare daily study time through a live leaderboard.
- **Live Activity Indicators:** Active users are identified with a pulsing status indicator during study sessions.
- **Dashboard Analytics:** Monitor pending tasks, overdue tasks and overall task completion percentage.
- **Study Streaks:** Track consecutive days of study alongside your current leaderboard ranking.

---
## Project Architecture

The application follows a modular Flask architecture, using Blueprints to separate features into logical components. SQLAlchemy provides the object-relational mapping (ORM) for the SQLite database, while Flask-Login manages user authentication and secure session handling.

```
orario/
├── app.py                  # Application entry point and main routes
├── models.py               # SQLAlchemy database models
├── routes/
│   ├── auth.py             # Login, registration and authentication
│   ├── dashboard.py        # Dashboard and analytics
│   ├── tasks.py            # Task management and calendar
│   ├── pomodoro.py         # Study timer and streak tracking, study groups and leaderboard
│   └── genai.py            # AI flashcard generation     
├── templates/              # Jinja2 HTML templates
├── utils/
│   └── utils.py            # Helper functions
├── static/
│   ├── css/                # All styling files
│   ├── js/                 # All javascript files
│   └── img/                # Images used throughout application
├── tests/                  # Automated pytest test suite
├── requirements.txt        # Requirements for the project
└── README.md
```

---

## Tech Stack
**Frontend**

![HTML5](https://img.shields.io/badge/html5-000000?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-orange?style=for-the-badge&logo=css&logoColor=black)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**Backend**

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-black?style=for-the-badge&logo=flask&logoColor=red)

**Database**

![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-green?style=for-the-badge&logo=sqlalchemy&logoColor=white)

**AI Integration**

![Groq](https://img.shields.io/badge/Groq-000000?style=for-the-badge&logo=groq&logoColor=white)

**Testing**

![Pytest](https://img.shields.io/badge/pytest-purple?style=for-the-badge&logo=pytest&logoColor=white)

---

## Installation & Setup

Follow these steps to configure and run the application locally:

### 1. Clone the Repository
```bash
git clone https://github.com/michaela357/orario-ATP3.git
cd orario-ATP3
```
### 2. Set up a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a .env file in the root directory containing:

```
GROQ_API_KEY=your_llm_api_key_here
```

### 5. Seed the database with the test data
``` Bash
python seed.py
```

### 6. Run the Application
``` Bash
python app.py
```
Open your browser and navigate to https://127.0.0.1:5000/.

## Evaluation Login Credentials

The repository includes seeded demonstration data, allowing evaluators to explore dashboard analytics, study statistics, streaks and personalised dashboard content without creating a new account.

* **Email:** `teacher@test.com`
* **Password:** `Password123!`
