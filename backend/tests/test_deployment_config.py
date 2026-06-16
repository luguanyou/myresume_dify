from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_docker_compose_runs_mysql_inside_the_stack():
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "  mysql:" in compose
    assert "image: mysql:8.4" in compose
    assert "MYSQL_HOST: mysql" in compose
    assert "MYSQL_ROOT_PASSWORD" in compose
    assert "condition: service_healthy" in compose
    assert "mysql_data:" in compose


def test_backend_dockerfile_does_not_pull_uv_from_ghcr():
    dockerfile = (REPO_ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")

    assert "ghcr.io/astral-sh/uv" not in dockerfile
    assert "requirements.txt" in dockerfile


def test_frontend_dockerfile_allows_fast_npm_registry():
    dockerfile = (REPO_ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")

    assert "ARG NPM_CONFIG_REGISTRY" in dockerfile
    assert "npm ci --registry=$NPM_CONFIG_REGISTRY" in dockerfile
