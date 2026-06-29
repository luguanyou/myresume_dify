from pathlib import Path

from sqlalchemy.engine import make_url

from app.core.config import Settings


def test_settings_load_env_file_from_backend_root() -> None:
    env_file = Settings.model_config["env_file"]

    assert Path(env_file).is_absolute()
    assert Path(env_file).name == ".env"
    assert Path(env_file).parent.name == "backend"


def test_database_url_escapes_special_characters_in_password() -> None:
    settings = Settings(
        mysql_host="db.example.test",
        mysql_port=3307,
        mysql_database="portfolio",
        mysql_user="root",
        mysql_password="Lgy@2026",
    )

    url = make_url(settings.database_url)

    assert url.host == "db.example.test"
    assert url.port == 3307
    assert url.username == "root"
    assert url.password == "Lgy@2026"
    assert url.database == "portfolio"
