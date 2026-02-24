# Hackathon Matcher

Double opt-in partner matching system for hackathon participants. Supports 150 users with concurrency-safe matching, admin dashboard, and email notifications.

## Installation

```bash
# Clone and enter the project
cd hackathon-matcher

# Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# Copy environment configuration
cp .env.example .env
```

## Configuration

Edit `.env` with your values:

| Variable | Description | Default |
|----------|-------------|---------|
| `SESSION_SECRET_KEY` | JWT signing key (change this!) | `change-me-to-a-random-secret-key` |
| `ADMIN_USERNAME` | Admin login username | `admin` |
| `ADMIN_PASSWORD` | Admin login password | `change-me-to-a-strong-password` |
| `BASE_URL` | Public URL for email links | `http://localhost:8000` |
| `EMAIL__ENABLED` | Enable SMTP sending | `false` |
| `EMAIL__SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL__SMTP_PORT` | SMTP port | `587` |
| `EMAIL__SMTP_USERNAME` | SMTP auth user | `` |
| `EMAIL__SMTP_PASSWORD` | SMTP auth password | `` |
| `EMAIL__FROM_ADDRESS` | Sender email | `hackathon@example.com` |
| `DATABASE__PATH` | SQLite file path | `hackathon_matcher.db` |

### Excel Column Mapping

Default columns match the standard Hebrew template: `שם מלא`, `מספר זהות`, `email`, `סטטוס שידוך`, `סניף מכינה`, `כיתה`.

To override column names, configure via env vars:

```
EXCEL__COLUMN_ID_NUMBER="מספר זהות"
EXCEL__COLUMN_EMAIL=email
EXCEL__COLUMN_FULL_NAME="שם מלא"
EXCEL__COLUMN_BRANCH="סניף מכינה"
EXCEL__COLUMN_CLASS_NAME="כיתה"
```

## Running

```bash
# Activate venv
source .venv/bin/activate

# Start the server
uvicorn src.app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

## Docker

```bash
# Copy and edit environment configuration
cp .env.example .env

# Build and start
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

SQLite data persists in a Docker volume (`hackathon-data`).

## Usage

### Admin Setup
1. Go to http://localhost:8000/#/admin
2. Login with admin credentials
3. Upload the Excel file with participant data
4. Set the matching deadline (optional)

### User Flow
1. Go to http://localhost:8000
2. Login with ID number + email (from the uploaded Excel)
3. Select a partner from the dropdown
4. Wait for partner to approve via email link
5. Once approved, both users see each other's contact info

### Cancellation
Only the person who initiated the match can cancel it (even after approval).

## Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test tier
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

## Linting

```bash
ruff check .
ruff format .
```

## Architecture

- **Backend:** FastAPI with repository pattern and dependency injection
- **Database:** SQLite with WAL mode and optimistic locking for concurrency
- **Frontend:** Vanilla JS SPA with Tailwind CSS, Hebrew RTL
- **Email:** Jinja2 templates, aiosmtplib (SMTP/SendGrid/Brevo compatible)
- **Auth:** JWT session tokens via httpOnly cookies
- **Concurrency:** `BEGIN IMMEDIATE` transactions + `WHERE status='available'` guard
