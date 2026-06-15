# AI Resume Portfolio

React + Vite + TypeScript frontend and FastAPI backend skeleton for the AI resume portfolio project.

## Project Structure

```text
frontend/   React + Vite + TypeScript app
backend/    FastAPI app and tests
.env.example
```

## 1. Verify The Frontend Skeleton

```bash
cd frontend
npm install
npm run build
```

Expected result: Vite builds the TypeScript app into `frontend/dist`.

## 2. Verify The Backend Skeleton

```bash
cd backend
uv sync
uv run pytest
```

Expected result: the health endpoint test passes.

## 3. Configure Local Environment

```bash
copy .env.example .env
```

Then replace placeholder values in `.env` with local development values. Do not commit real secrets.

Verification: confirm `.env` exists locally and `.env.example` only contains placeholders such as `replace_with_your_dify_api_key`.

## 4. Start The Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verification:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "portfolio-api",
    "version": "1.0"
  },
  "message": "ok"
}
```

## 5. Start The Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

Verification: open the Vite local URL, usually `http://localhost:5173`, and check that the Health card reports `API connected` while the backend is running.

## 6. Local Development Notes

- Frontend dev server proxies `/api` to `http://127.0.0.1:8000`.
- Backend app entrypoint is `backend/app/main.py`.
- Health route lives in `backend/app/api/health.py`.
- Shared backend settings live in `backend/app/core/config.py`.

## 7. Docker Deployment

This project can run the frontend and backend in Docker while keeping MySQL installed directly on the server.

For a first-time production deployment, follow the step-by-step runbook in [DEPLOYMENT.md](DEPLOYMENT.md).

Create a production `.env` from the example:

```bash
copy .env.example .env
```

For Docker, keep the backend database host pointed at the server host:

```env
DOCKER_MYSQL_HOST=host.docker.internal
MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=your_mysql_password
FRONTEND_PORT=8080
DOCKER_CORS_ORIGINS=http://your-domain-or-server-ip:8080
```

Start or update the containers:

```bash
docker compose up -d --build
```

Open:

```text
http://your-server-ip:8080
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Initialize or seed the host MySQL database from inside the backend container:

```bash
docker compose exec backend python scripts/init_db.py
```

Notes:

- The frontend container serves the built React app with Nginx.
- Nginx inside the frontend container proxies `/api` and `/uploads` to the backend container.
- Backend uploads are persisted through `./backend/uploads:/app/uploads`.
- Do not expose MySQL to the public internet; allow only local/server Docker network access.
