# ClipMind AI Frontend

Next.js UI for Module 1:
- Registration
- Login
- Role selection
- Dashboard
- Video upload validation
- Upload history
- Processing status UI

## Run

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Backend integration

Replace the demo localStorage logic with FastAPI endpoints such as:

POST /auth/register
POST /auth/login
GET /users/me
POST /videos/upload
GET /videos
GET /videos/{id}

The frontend is intentionally API-ready but uses localStorage for the first UI demo.
