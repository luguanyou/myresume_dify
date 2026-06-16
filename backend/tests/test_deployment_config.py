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
