# Backend

FastAPI service for the AI resume portfolio.

## Install

```bash
uv sync
```

Verification: `uv run python -c "import app.main; print('ok')"` prints `ok`.

## Test

```bash
uv run pytest
```

Verification: `tests/test_health.py` passes.

## Initialize Local MySQL

Configure MySQL in `.env`, then initialize the database, tables, and MVP data:

```bash
uv run python scripts/init_db.py
```

The script does this for you:

1. Creates the configured MySQL database if it does not exist.
2. Creates the SQLAlchemy tables.
3. Inserts 3 projects, current resume metadata, site profile, prompt questions, and an admin account.

Defaults are `admin` / `admin123`; override with `SEED_ADMIN_USERNAME` and `SEED_ADMIN_PASSWORD`.

If the database already exists and you only want to re-run table/data seed:

```bash
uv run python scripts/seed.py
```

## Run

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verification: request `http://127.0.0.1:8000/api/health` and confirm `data.status` is `ok`.
