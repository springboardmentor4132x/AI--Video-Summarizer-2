# ClipMind AI 🚀
### Video Summarization & Key Moments Detection Platform

ClipMind AI is an intelligent web application designed to help users consume long-form videos efficiently by extracting transcripts, generating concise AI summaries, and detecting key video moments with timestamps.

---

## 📌 Module 1 — Core Infrastructure & Authentication

Module 1 sets up the core foundation of ClipMind AI:

- **User Registration**: Register new user accounts with full name, email, password, and system role.
- **Secure Authentication**: Passwords hashed securely using `bcrypt`.
- **JWT Authentication**: Json Web Tokens (JWT) issued upon login to secure all private backend APIs.
- **Role-Based Access Control (RBAC)**: Enforces access restrictions across 4 distinct user roles:
  - 🎥 **Content Creator**: Uploads videos, manages transcripts, and views content analytics.
  - 🎓 **Learner**: Watches videos, reads summaries, searches transcripts, and saves highlights.
  - 👩‍🏫 **Educator**: Prepares educational lecture summaries and tracks classroom engagement.
  - 🛠️ **Administrator**: Oversees users, AI processing pipelines, and system configuration.
- **Database Storage**: PostgreSQL database managed cleanly with SQLAlchemy ORM models.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Security & Auth**: JWT (`python-jose`), Password Hashing (`bcrypt`)


---

## 📂 Folder Structure

```text
ClipMind-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── database.py      # SQLAlchemy database connection & session setup
│   │   ├── models.py        # Database ORM models (User, Video)
│   │   ├── schemas.py       # Pydantic data validation schemas
│   │   ├── auth.py          # JWT creation, bcrypt hashing & RBAC logic
│   │   └── routes/
│   │       └── auth_routes.py # Auth endpoints (/register, /login, /me)
│   ├── .env                 # Environment configuration (Database URL, JWT Secret)
│   └── requirements.txt     # Python backend dependencies
│
├── frontend/                # React / Next.js user interface (coming next)
├── tests/
│   └── test_auth.py         # Automated authentication integration test suite
└── README.md
```

---

## 🚀 How to Set Up and Run

### 1. Navigating to the Backend
Open your terminal in the project directory and move into `backend`:
```bash
cd backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database & Environment
Make sure `.env` contains your PostgreSQL connection string and secret key:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/clipmind_db
JWT_SECRET_KEY=your_random_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Start the Backend Server
```bash
uvicorn app.main:app --reload
```
or run using Python directly:
```bash
python -m uvicorn app.main:app --reload
```

---

## 🌐 API Endpoints & Testing

Once the server is running, open your browser and navigate to:
👉 **`http://127.0.0.1:8000/docs`**

| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user account | Public |
| `POST` | `/auth/login` | Log in with email & password, returns JWT token | Public |
| `GET` | `/auth/me` | Retrieve currently logged-in user profile | Authenticated |
| `GET` | `/auth/admin-check` | Demo endpoint for testing RBAC | Administrator Only |

---

## 🧪 Running Automated Tests

To run the full authentication test suite:
```bash
python tests/test_auth.py
```
