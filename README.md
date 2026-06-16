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

This project can run the frontend, backend, and MySQL together with Docker Compose. This is the simplest deployment path because you do not need an existing remote database password.

For a first-time production deployment, follow the step-by-step runbook in [DEPLOYMENT.md](DEPLOYMENT.md).

Create a production `.env` from the example:

```bash
copy .env.example .env
```

For Docker, choose new database passwords instead of trying to recover an old one:

```env
MYSQL_PORT=3306
MYSQL_DATABASE=portfolio
MYSQL_USER=portfolio_user
MYSQL_PASSWORD=your_new_mysql_password
MYSQL_ROOT_PASSWORD=your_new_mysql_root_password
FRONTEND_PORT=8080
DOCKER_CORS_ORIGINS=http://your-domain-or-server-ip:8080
APP_ROOT_PATH=/dify
PUBLIC_API_BASE_URL=/dify/api
PUBLIC_UPLOAD_BASE_URL=/dify/uploads
VITE_API_BASE_URL=/dify/api
VITE_APP_BASE_PATH=/dify/
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
NPM_CONFIG_REGISTRY=https://registry.npmmirror.com
```

Start or update the containers:

```bash
docker compose up -d --build
```

Open:

```text
http://your-server-ip:8080/dify/
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Initialize or seed the MySQL database from inside the backend container:

```bash
docker compose exec backend python scripts/init_db.py
```

Notes:

- The frontend container serves the built React app with Nginx.
- Nginx inside the frontend container proxies `/api` and `/uploads` to the backend container.
- MySQL runs inside Docker Compose and persists data in the `mysql_data` Docker volume.
- Backend uploads are persisted through `./backend/uploads:/app/uploads`.
- MySQL is not published to the public internet.
- The public app, API, uploads, and docs are served under the `/dify` URL prefix.
- `PIP_INDEX_URL` and `NPM_CONFIG_REGISTRY` can be changed if your server has a faster package mirror.
