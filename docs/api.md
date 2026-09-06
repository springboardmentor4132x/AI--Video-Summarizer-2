# API (Milestone 1)

Base URL: `http://localhost:8000`

| Method | Path | Notes |
|---|---|---|
| POST | `/auth/register` | learner / content_creator / educator |
| POST | `/auth/login` | JWT |
| GET/PATCH | `/users/me` | Profile |
| GET | `/users` | Admin only |
| POST | `/videos/upload` | multipart file |
| GET | `/videos` | Library |
| GET/PATCH/DELETE | `/videos/{id}` | Detail |
| POST | `/videos/{id}/process` | Queue FFmpeg |
| GET | `/videos/{id}/jobs` | Job list |
| GET | `/videos/{id}/stream` | Playback (`?token=`) |
| GET | `/videos/{id}/thumbnail` | JPEG (`?token=`) |
| GET | `/jobs/{id}` | Single job |
| GET | `/health` | Liveness |

Interactive docs: http://localhost:8000/docs
