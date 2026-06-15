import sys
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from scripts.seed import seed_database


def build_mysql_server_url(user: str, password: str, host: str, port: int) -> str:
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/?charset=utf8mb4"
    )


def quote_mysql_identifier(identifier: str) -> str:
    if not identifier:
        raise ValueError("MySQL database name cannot be empty")
    return f"`{identifier.replace('`', '``')}`"


def build_create_database_sql(database_name: str) -> str:
    return (
        f"CREATE DATABASE IF NOT EXISTS {quote_mysql_identifier(database_name)} "
        "DEFAULT CHARACTER SET utf8mb4 "
        "DEFAULT COLLATE utf8mb4_unicode_ci"
    )


def format_mysql_connection_error(
    error: OperationalError,
    user: str,
    host: str,
    port: int,
    database: str,
) -> str:
    original = getattr(error, "orig", error)
    code = original.args[0] if getattr(original, "args", None) else None
    reason = original.args[1] if getattr(original, "args", None) and len(original.args) > 1 else str(original)

    if code == 1045:
        hint = (
            "Access denied. MySQL rejected the configured user/password, or the user does not exist.\n"
            "Create or update backend/.env with the MySQL account you can log in with, for example:\n"
            f"MYSQL_HOST={host}\n"
            f"MYSQL_PORT={port}\n"
            f"MYSQL_DATABASE={database}\n"
            f"MYSQL_USER={user}\n"
            "MYSQL_PASSWORD=your_mysql_password\n"
            "\n"
            "If you use WAMP locally, this is often MYSQL_USER=root with your WAMP MySQL password."
        )
    elif code == 2003:
        hint = "Cannot connect to MySQL. Check that the MySQL service is running and the host/port are correct."
    else:
        hint = "MySQL connection failed. Check backend/.env and your MySQL service."

    return f"{hint}\n\nOriginal MySQL error: {code} {reason}"


def create_database_if_missing() -> None:
    server_url = build_mysql_server_url(
        user=settings.mysql_user,
        password=settings.mysql_password,
        host=settings.mysql_host,
        port=settings.mysql_port,
    )
    server_engine = create_engine(server_url, pool_pre_ping=True)
    try:
        with server_engine.begin() as connection:
            connection.execute(text(build_create_database_sql(settings.mysql_database)))
    except OperationalError as exc:
        raise SystemExit(
            format_mysql_connection_error(
                exc,
                user=settings.mysql_user,
                host=settings.mysql_host,
                port=settings.mysql_port,
                database=settings.mysql_database,
            )
        ) from exc
    finally:
        server_engine.dispose()
    print(f"MySQL database ready: {settings.mysql_database}")


def main() -> None:
    create_database_if_missing()
    seed_database()


if __name__ == "__main__":
    main()
