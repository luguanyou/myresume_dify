import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import AdminUser, MediaAsset, Project, PromptQuestion, ResumeFile, SiteProfile
from app.security import hash_password


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "uploads"))
    monkeypatch.setattr(settings, "public_upload_base_url", "/uploads")

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"%PDF-1.4\n%test resume\n%%EOF\n")

    with testing_session_local() as db:
        first_project = Project(
            slug="backend-portfolio-api",
            title="Portfolio Backend API",
            subtitle="FastAPI portfolio service",
            summary="Public portfolio API backed by SQLAlchemy models.",
            project_type="Backend",
            background="A resume site needs structured project and resume data.",
            goals="Expose public content and protect admin operations.",
            role="Backend architecture and API implementation.",
            features=["Public project list", "Admin authentication"],
            challenges=["Token verification"],
            solutions=["Signed bearer token"],
            tech_stack=["FastAPI", "SQLAlchemy", "MySQL"],
            links=[{"label": "Repo", "url": "https://example.com/repo", "link_type": "github"}],
            is_featured=True,
            sort_order=100,
            status="published",
        )
        second_project = Project(
            slug="frontend-portfolio-ui",
            title="Portfolio Frontend UI",
            summary="Responsive React portfolio experience.",
            project_type="Frontend",
            tech_stack=["React", "Vite"],
            is_featured=False,
            sort_order=90,
            status="published",
        )
        hidden_project = Project(
            slug="hidden-draft",
            title="Hidden Draft",
            summary="This should not be public.",
            project_type="Draft",
            tech_stack=["Python"],
            is_featured=True,
            sort_order=200,
            status="hidden",
        )
        db.add_all([first_project, second_project, hidden_project])
        db.flush()

        cover = MediaAsset(
            project_id=first_project.id,
            media_type="image",
            purpose="cover",
            original_filename="cover.png",
            stored_filename="cover.png",
            storage_path="uploads/projects/cover.png",
            public_url="/uploads/projects/cover.png",
            mime_type="image/png",
            file_ext="png",
            file_size=128,
            alt_text="Cover screenshot",
            sort_order=100,
            status="published",
        )
        resume_media = MediaAsset(
            media_type="document",
            purpose="resume",
            original_filename="resume.pdf",
            stored_filename="resume.pdf",
            storage_path=str(resume_path),
            public_url="/uploads/resume/resume.pdf",
            mime_type="application/pdf",
            file_ext="pdf",
            file_size=resume_path.stat().st_size,
            alt_text="Current resume",
            status="published",
        )
        db.add_all([cover, resume_media])
        db.flush()
        first_project.cover_media_id = cover.id

        db.add(
            ResumeFile(
                title="Current Resume",
                media_id=resume_media.id,
                version_label="test",
                is_current=True,
                status="published",
            )
        )
        db.add(
            SiteProfile(
                owner_name="Tester",
                headline="AI Application Developer",
                summary="Builds portfolio products.",
                email="tester@example.com",
                github_url="https://github.com/example",
                portfolio_url="https://example.com",
                extra_links=[],
                status="published",
            )
        )
        db.add_all(
            [
                PromptQuestion(
                    question="What role are you best suited for?",
                    category="positioning",
                    sort_order=100,
                    status="published",
                ),
                PromptQuestion(
                    question="Hidden question",
                    category="draft",
                    sort_order=200,
                    status="hidden",
                ),
            ]
        )
        db.add(
            AdminUser(
                username="admin",
                password_hash=hash_password("admin123"),
                display_name="Admin",
                email="admin@example.com",
                status="active",
            )
        )
        db.commit()

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def admin_headers(client):
    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_public_project_list_and_detail(client):
    list_response = client.get("/api/projects")

    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["success"] is True
    assert [project["slug"] for project in list_body["data"]] == [
        "backend-portfolio-api",
        "frontend-portfolio-ui",
    ]
    assert list_body["data"][0]["cover_media"]["url"] == "/uploads/projects/cover.png"

    featured_response = client.get("/api/projects", params={"featured": True})
    assert [project["slug"] for project in featured_response.json()["data"]] == ["backend-portfolio-api"]

    project_id = list_body["data"][0]["id"]
    detail_response = client.get(f"/api/projects/{project_id}")

    assert detail_response.status_code == 200
    detail = detail_response.json()["data"]
    assert detail["features"] == ["Public project list", "Admin authentication"]
    assert detail["tech_stack"] == ["FastAPI", "SQLAlchemy", "MySQL"]
    assert detail["media"][0]["url"] == "/uploads/projects/cover.png"


def test_resume_profile_and_prompt_public_endpoints(client):
    resume_response = client.get("/api/resume/current")
    assert resume_response.status_code == 200
    assert resume_response.json()["data"]["download_url"] == "/api/resume/download"

    download_response = client.get("/api/resume/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
    assert download_response.content.startswith(b"%PDF")

    profile_response = client.get("/api/site/profile")
    assert profile_response.status_code == 200
    assert profile_response.json()["data"]["owner_name"] == "Tester"

    questions_response = client.get("/api/prompt-questions")
    assert questions_response.status_code == 200
    assert [item["question"] for item in questions_response.json()["data"]] == [
        "What role are you best suited for?"
    ]


def test_resume_download_url_uses_configured_api_base(client, monkeypatch):
    monkeypatch.setattr(settings, "public_api_base_url", "/dify/api")

    resume_response = client.get("/api/resume/current")

    assert resume_response.status_code == 200
    assert resume_response.json()["data"]["download_url"] == "/dify/api/resume/download"


def test_admin_login_and_me_require_valid_bearer_token(client):
    anonymous_response = client.get("/api/admin/auth/me")
    assert anonymous_response.status_code == 401
    assert anonymous_response.json()["success"] is False
    assert anonymous_response.json()["error"]["code"] == "UNAUTHORIZED"

    anonymous_projects_response = client.get("/api/admin/projects")
    assert anonymous_projects_response.status_code == 401

    bad_login_response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert bad_login_response.status_code == 401

    login_response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert login_response.status_code == 200
    login_data = login_response.json()["data"]
    assert login_data["token_type"] == "bearer"
    assert login_data["admin"]["username"] == "admin"
    assert "password_hash" not in login_data["admin"]

    me_response = client.get(
        "/api/admin/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["data"]["username"] == "admin"

    admin_projects_response = client.get(
        "/api/admin/projects",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )

    assert admin_projects_response.status_code == 200
    assert admin_projects_response.json()["data"][0]["slug"] == "hidden-draft"


def test_admin_project_crud_requires_token_and_updates_public_visibility(client):
    project_payload = {
        "slug": "admin-created-project",
        "title": "Admin Created Project",
        "subtitle": "Managed through API",
        "summary": "Created by an authenticated admin request.",
        "project_type": "Backend",
        "background": "Admin content needs CRUD APIs.",
        "goals": "Exercise create, update, hide, feature, sort, and delete.",
        "role": "API implementation.",
        "features": ["Create", "Update"],
        "challenges": ["Auth"],
        "solutions": ["Bearer token"],
        "tech_stack": ["FastAPI", "SQLAlchemy"],
        "links": [],
        "is_featured": True,
        "sort_order": 120,
        "status": "published",
    }

    anonymous_create = client.post("/api/admin/projects", json=project_payload)
    assert anonymous_create.status_code == 401

    headers = admin_headers(client)
    create_response = client.post("/api/admin/projects", json=project_payload, headers=headers)

    assert create_response.status_code == 200
    created = create_response.json()["data"]
    assert created["slug"] == "admin-created-project"
    assert created["is_featured"] is True
    assert created["sort_order"] == 120

    detail_response = client.get(f"/api/admin/projects/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["features"] == ["Create", "Update"]

    public_slugs = [project["slug"] for project in client.get("/api/projects").json()["data"]]
    assert "admin-created-project" in public_slugs

    update_response = client.put(
        f"/api/admin/projects/{created['id']}",
        json={"title": "Hidden Admin Project", "status": "hidden", "is_featured": False, "sort_order": 5},
        headers=headers,
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["title"] == "Hidden Admin Project"
    assert updated["status"] == "hidden"
    assert updated["is_featured"] is False
    assert updated["sort_order"] == 5

    public_slugs_after_hide = [project["slug"] for project in client.get("/api/projects").json()["data"]]
    assert "admin-created-project" not in public_slugs_after_hide

    delete_response = client.delete(f"/api/admin/projects/{created['id']}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["deleted"] is True

    missing_response = client.get(f"/api/admin/projects/{created['id']}", headers=headers)
    assert missing_response.status_code == 404


def test_admin_media_crud_uploads_edits_and_soft_deletes_files(client):
    headers = admin_headers(client)
    project_id = client.get("/api/admin/projects", headers=headers).json()["data"][0]["id"]

    anonymous_list = client.get("/api/admin/media")
    assert anonymous_list.status_code == 401

    upload_response = client.post(
        "/api/admin/media",
        data={"media_type": "image", "purpose": "screenshot", "project_id": str(project_id), "alt_text": "Before"},
        files={"file": ("screenshot.png", b"\x89PNG\r\n\x1a\nimage", "image/png")},
        headers=headers,
    )
    assert upload_response.status_code == 200
    media = upload_response.json()["data"]
    assert media["media_type"] == "image"
    assert media["project_id"] == project_id
    assert media["alt_text"] == "Before"
    assert media["url"].startswith("/uploads/projects/")

    public_file_response = client.get(media["url"])
    assert public_file_response.status_code == 200
    assert public_file_response.headers["content-type"] == "image/png"

    detail_response = client.get(f"/api/admin/media/{media['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["original_filename"] == "screenshot.png"

    list_response = client.get("/api/admin/media", params={"project_id": project_id}, headers=headers)
    assert list_response.status_code == 200
    assert media["id"] in [item["id"] for item in list_response.json()["data"]]

    update_response = client.put(
        f"/api/admin/media/{media['id']}",
        json={"alt_text": "After", "purpose": "cover", "sort_order": 30},
        headers=headers,
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["alt_text"] == "After"
    assert updated["purpose"] == "cover"
    assert updated["sort_order"] == 30

    delete_response = client.delete(f"/api/admin/media/{media['id']}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["deleted"] is True

    list_after_delete = client.get("/api/admin/media", params={"project_id": project_id}, headers=headers)
    assert media["id"] not in [item["id"] for item in list_after_delete.json()["data"]]


def test_admin_resume_upload_list_and_set_current(client):
    headers = admin_headers(client)

    anonymous_list = client.get("/api/admin/resumes")
    assert anonymous_list.status_code == 401

    first_upload = client.post(
        "/api/admin/resumes",
        data={"title": "Resume V1", "version_label": "v1", "set_current": "true"},
        files={"file": ("resume-v1.pdf", b"%PDF-1.4\nv1\n%%EOF\n", "application/pdf")},
        headers=headers,
    )
    assert first_upload.status_code == 200
    first_resume = first_upload.json()["data"]
    assert first_resume["title"] == "Resume V1"
    assert first_resume["is_current"] is True

    second_upload = client.post(
        "/api/admin/resumes",
        data={"title": "Resume V2", "version_label": "v2", "set_current": "false"},
        files={"file": ("resume-v2.pdf", b"%PDF-1.4\nv2\n%%EOF\n", "application/pdf")},
        headers=headers,
    )
    assert second_upload.status_code == 200
    second_resume = second_upload.json()["data"]
    assert second_resume["is_current"] is False

    current_response = client.put(f"/api/admin/resumes/{second_resume['id']}/current", headers=headers)
    assert current_response.status_code == 200
    assert current_response.json()["data"]["is_current"] is True

    resumes_response = client.get("/api/admin/resumes", headers=headers)
    assert resumes_response.status_code == 200
    current_ids = [item["id"] for item in resumes_response.json()["data"] if item["is_current"]]
    assert current_ids == [second_resume["id"]]

    public_resume = client.get("/api/resume/current")
    assert public_resume.json()["data"]["id"] == second_resume["id"]


def test_admin_site_profile_read_and_update(client):
    headers = admin_headers(client)

    anonymous_read = client.get("/api/admin/site/profile")
    assert anonymous_read.status_code == 401

    read_response = client.get("/api/admin/site/profile", headers=headers)
    assert read_response.status_code == 200
    assert read_response.json()["data"]["owner_name"] == "Tester"

    update_response = client.put(
        "/api/admin/site/profile",
        json={
            "owner_name": "Updated Tester",
            "headline": "Principal AI Builder",
            "summary": "Updated summary",
            "email": "updated@example.com",
            "phone": "123",
            "wechat": "tester-wechat",
            "github_url": "https://github.com/updated",
            "portfolio_url": "https://portfolio.example.com",
            "extra_links": [{"label": "Blog", "url": "https://blog.example.com"}],
            "status": "published",
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["owner_name"] == "Updated Tester"

    public_profile = client.get("/api/site/profile")
    assert public_profile.json()["data"]["owner_name"] == "Updated Tester"


def test_admin_prompt_question_crud_requires_token(client):
    anonymous_create = client.post(
        "/api/admin/prompt-questions",
        json={"question": "What can you ship?", "category": "proof", "sort_order": 50, "status": "published"},
    )
    assert anonymous_create.status_code == 401

    headers = admin_headers(client)
    create_response = client.post(
        "/api/admin/prompt-questions",
        json={"question": "What can you ship?", "category": "proof", "sort_order": 50, "status": "published"},
        headers=headers,
    )
    assert create_response.status_code == 200
    created = create_response.json()["data"]
    assert created["question"] == "What can you ship?"

    list_response = client.get("/api/admin/prompt-questions", headers=headers)
    assert created["id"] in [item["id"] for item in list_response.json()["data"]]

    update_response = client.put(
        f"/api/admin/prompt-questions/{created['id']}",
        json={"question": "What can you ship next?", "status": "hidden", "sort_order": 10},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["question"] == "What can you ship next?"
    assert update_response.json()["data"]["status"] == "hidden"

    public_questions = [item["question"] for item in client.get("/api/prompt-questions").json()["data"]]
    assert "What can you ship next?" not in public_questions

    delete_response = client.delete(f"/api/admin/prompt-questions/{created['id']}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["deleted"] is True

    read_deleted = client.get(f"/api/admin/prompt-questions/{created['id']}", headers=headers)
    assert read_deleted.status_code == 404
