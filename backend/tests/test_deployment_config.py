from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_docker_compose_uses_host_mysql_instead_of_mysql_container():
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    backend_section = compose.split("  backend:", 1)[1].split("  frontend:", 1)[0]

    assert "  mysql:" not in compose
    assert "image: mysql:" not in compose
    assert "MYSQL_ROOT_PASSWORD" not in compose
    assert "mysql_data:" not in compose
    assert "MYSQL_HOST: ${MYSQL_HOST:-host.docker.internal}" in backend_section
    assert 'host.docker.internal:host-gateway' in backend_section
    assert "depends_on:" not in backend_section
    assert "APP_ROOT_PATH: ${APP_ROOT_PATH:-/dify}" in compose
    assert "PUBLIC_UPLOAD_BASE_URL: ${PUBLIC_UPLOAD_BASE_URL:-/dify/uploads}" in compose
    assert "VITE_API_BASE_URL: ${VITE_API_BASE_URL:-/dify/api}" in compose
    assert "VITE_APP_BASE_PATH: ${VITE_APP_BASE_PATH:-/dify/}" in compose


def test_backend_compose_loads_runtime_secrets_from_root_env_file():
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    backend_section = compose.split("  backend:", 1)[1].split("  frontend:", 1)[0]

    assert "env_file:" in backend_section
    assert "- ./.env" in backend_section
    assert "DIFY_API_KEY:" not in backend_section
    assert "DIFY_API_BASE_URL:" not in backend_section


def test_backend_dockerfile_does_not_pull_uv_from_ghcr():
    dockerfile = (REPO_ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")

    assert "ghcr.io/astral-sh/uv" not in dockerfile
    assert "requirements.txt" in dockerfile


def test_frontend_dockerfile_allows_fast_npm_registry():
    dockerfile = (REPO_ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")

    assert "ARG NPM_CONFIG_REGISTRY" in dockerfile
    assert "npm ci --registry=$NPM_CONFIG_REGISTRY" in dockerfile
    assert "ARG VITE_APP_BASE_PATH=/dify/" in dockerfile


def test_vite_dev_server_proxies_upload_paths():
    vite_config = (REPO_ROOT / "frontend" / "vite.config.ts").read_text(encoding="utf-8")

    assert "'/dify/uploads'" in vite_config
    assert "target: 'http://127.0.0.1:8000'" in vite_config


def test_nginx_serves_app_under_dify_prefix_and_proxies_backend_routes():
    nginx = (REPO_ROOT / "frontend" / "nginx.conf").read_text(encoding="utf-8")

    assert "location = /dify" in nginx
    assert "location /dify/api/" in nginx
    assert "proxy_pass http://backend:8000/api/" in nginx
    assert "location /dify/uploads/" in nginx
    assert "location /dify/docs" in nginx
    assert "location /dify/redoc" in nginx
    assert "location /dify/openapi.json" in nginx
    assert "location /dify/" in nginx
    assert "location /api/" in nginx
    assert "location /uploads/" in nginx
    assert "return 404;" in nginx
