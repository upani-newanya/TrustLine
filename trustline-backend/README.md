# TrustLine Backend

Production-structured FastAPI backend for **TrustLine**, a Cyber Crime Reporting and Security System for Sri Lanka.

## Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Pydantic
- JWT authentication
- bcrypt password hashing
- Alembic-ready model structure
- Local evidence upload storage

## Project Structure

```text
trustline-backend/
  app/
    main.py
    core/
    models/
    schemas/
    api/
    services/
    utils/
    uploads/evidence/
  requirements.txt
  .env.example
  README.md
  run.py
```

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies.
3. Create `.env` from `.env.example`.
4. Run the app.

```bash
pip install -r requirements.txt
cp .env.example .env
python run.py
```

App base URL: `http://localhost:8000`

Interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `UPLOAD_DIR`
- `MAX_UPLOAD_SIZE_MB`

## Key Features Implemented

- Role-based access (`user`, `admin`, `guardian`)
- JWT auth and password hashing
- Complaint creation via manual form and chatbot flow
- Evidence upload with file type/size validation
- Complaint-based messaging between user and admin
- In-app notifications stored in DB
- Admin dashboard, queue, detail, assignment, status and priority updates, internal notes
- Resource categories and resource lookup by slug
- Audit logging for key actions:
  - login
  - complaint created
  - status changed
  - evidence uploaded
  - admin assigned

## Notes for Expansion

- Current startup uses `Base.metadata.create_all()` for local development.
- For production deployments, use Alembic migrations.
- Add test suite (`pytest`) and stricter validation rules before release.
