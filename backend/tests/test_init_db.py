import subprocess
import sys
from pathlib import Path

from pymysql.err import OperationalError as PyMySQLOperationalError
from sqlalchemy import create_engine, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import Project, PromptQuestion, SiteProfile
from scripts.init_db import build_create_database_sql, build_mysql_server_url, format_mysql_connection_error


def test_build_mysql_server_url_omits_database_name():
    url = build_mysql_server_url(
        user="portfolio_user",
        password="pass word",
        host="127.0.0.1",
        port=3306,
    )

    assert url == "mysql+pymysql://portfolio_user:pass+word@127.0.0.1:3306/?charset=utf8mb4"


def test_build_create_database_sql_escapes_database_identifier():
    sql = build_create_database_sql("portfolio")

    assert sql == (
        "CREATE DATABASE IF NOT EXISTS `portfolio` "
        "DEFAULT CHARACTER SET utf8mb4 "
        "DEFAULT COLLATE utf8mb4_unicode_ci"
    )


def test_format_mysql_connection_error_for_access_denied():
    original = PyMySQLOperationalError(1045, "Access denied for user 'portfolio_user'@'localhost'")
    error = OperationalError("connect", {}, original)

    message = format_mysql_connection_error(
        error,
        user="portfolio_user",
        host="127.0.0.1",
        port=3306,
        database="portfolio",
    )

    assert "Access denied" in message
    assert "MYSQL_USER=portfolio_user" in message
    assert "backend/.env" in message


def test_init_db_script_can_be_loaded_from_script_path():
    backend_root = Path(__file__).parents[1]
    script_path = backend_root / "scripts" / "init_db.py"
    scripts_dir = backend_root / "scripts"
    code = (
        "import runpy, sys; "
        f"root = {str(backend_root)!r}; "
        f"scripts = {str(scripts_dir)!r}; "
        "sys.path = [scripts] + [p for p in sys.path if p not in ('', root, scripts)]; "
        f"runpy.run_path({str(script_path)!r}, run_name='not_main')"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_seed_script_can_be_loaded_from_script_path():
    backend_root = Path(__file__).parents[1]
    script_path = backend_root / "scripts" / "seed.py"
    scripts_dir = backend_root / "scripts"
    code = (
        "import runpy, sys; "
        f"root = {str(backend_root)!r}; "
        f"scripts = {str(scripts_dir)!r}; "
        "sys.path = [scripts] + [p for p in sys.path if p not in ('', root, scripts)]; "
        f"runpy.run_path({str(script_path)!r}, run_name='not_main')"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_seed_database_replaces_mock_content_with_real_resume_content(tmp_path, monkeypatch):
    from scripts import seed

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with testing_session_local() as db:
        db.add_all(
            [
                Project(
                    slug="ai-resume-assistant",
                    title="AI Resume Assistant",
                    summary="Old mock project.",
                    project_type="AI Application",
                    tech_stack=["React"],
                    status="published",
                ),
                Project(
                    slug="responsive-portfolio-ui",
                    title="Responsive Portfolio UI",
                    summary="Old mock project.",
                    project_type="Frontend",
                    tech_stack=["React"],
                    status="published",
                ),
                PromptQuestion(
                    question="What role are you best suited for, and why?",
                    category="positioning",
                    sort_order=100,
                    status="published",
                ),
            ]
        )
        db.commit()

    resume_source = tmp_path / "real-resume.pdf"
    resume_source.write_bytes(b"%PDF-1.4\nreal resume\n%%EOF\n")
    monkeypatch.setenv("SEED_RESUME_SOURCE", str(resume_source))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(seed, "engine", engine)
    monkeypatch.setattr(seed, "SessionLocal", testing_session_local)

    seed.seed_database()

    with testing_session_local() as db:
        profile = db.scalar(select(SiteProfile))
        assert profile is not None
        assert profile.owner_name == "卢官有"
        assert profile.email == "923206295@qq.com"
        assert profile.phone == "18770919352"
        assert "RAG Agent" in profile.headline

        published_slugs = [
            project.slug
            for project in db.scalars(
                select(Project).where(Project.status == "published", Project.deleted_at.is_(None))
                .order_by(Project.sort_order.desc(), Project.id.asc())
            )
        ]
        assert published_slugs == [
            "orange-rag-agent",
            "agri-inventory-ledger",
            "warehouse-3d-digital-twin",
            "interactive-ai-resume-rag",
        ]

        old_project = db.scalar(select(Project).where(Project.slug == "responsive-portfolio-ui"))
        assert old_project is not None
        assert old_project.deleted_at is not None

        prompt_questions = [
            question.question
            for question in db.scalars(
                select(PromptQuestion).where(PromptQuestion.status == "published", PromptQuestion.deleted_at.is_(None))
                .order_by(PromptQuestion.sort_order.desc(), PromptQuestion.id.asc())
            )
        ]
        assert prompt_questions == [
            "请用 1 分钟介绍一下你的核心优势。",
            "你适合 AI 全栈研发岗位的理由是什么？",
            "讲讲脐橙农技 RAG Agent 如何降低大模型幻觉。",
            "农资店进销存系统如何保证库存和赊账数据一致？",
            "智能仓储 3D 可视化项目有哪些技术难点和业务价值？",
        ]

        old_question = db.scalar(
            select(PromptQuestion).where(PromptQuestion.question == "What role are you best suited for, and why?")
        )
        assert old_question is not None
        assert old_question.deleted_at is not None
