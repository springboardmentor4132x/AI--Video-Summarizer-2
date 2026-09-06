# Database

PostgreSQL schema, Alembic migrations, and seeds live here.

```
database/
  alembic.ini
  alembic/versions/     # schema versions
  seeds/seed_admin.py   # default admin
```

SQLAlchemy models still live in `backend/app/models` (app code). This folder owns the actual database history.

## Commands

From the repo root:

```bash
alembic -c database/alembic.ini upgrade head
alembic -c database/alembic.ini revision -m "describe change"
```

Default admin (seeded on API startup):

- Email: `admin@clipmind.ai`
- Password: `Admin123!`
