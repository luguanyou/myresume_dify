import os
import shutil
import sys
from pathlib import Path

from sqlalchemy import select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import AdminUser, MediaAsset, Project, PromptQuestion, ResumeFile, SiteProfile
from app.models.portfolio import utc_now
from app.security import hash_password, verify_password


PROJECTS = [
    {
        "slug": "orange-rag-agent",
        "title": "脐橙农技智能问诊 RAG Agent",
        "subtitle": "从模糊提问到精准农技开方的垂直领域智能问答系统",
        "summary": "针对大模型在农业诊断中易产生幻觉的问题，独立研发垂直领域智能问答系统，通过意图识别、槽位状态管理、本地知识库检索和 SSE 流式响应，实现从农户口语化提问到结构化农技建议的闭环。",
        "project_type": "AI / RAG Agent",
        "background": "农业问诊场景中，用户描述往往模糊，直接调用大模型容易在缺少树龄、症状等关键条件时给出不可靠结论。",
        "goals": "构建一个先追问关键变量、再检索专业知识库、最后综合生成建议的农技问诊 Agent，降低幻觉并提升回答可信度。",
        "role": "独立全栈开发，负责 Agent 工作流、知识库建模、FastAPI 后端、uni-app 前端、SSE 流式体验和运维接口。",
        "features": ["意图识别", "槽位提取与状态机管理", "缺失条件追问", "本地 ChromaDB 知识库", "SSE 流式输出", "历史对话日志审计"],
        "challenges": ["农业口语与专业术语存在语义鸿沟", "单轮 QA 容易产生幻觉", "移动端需要稳定解析流式响应"],
        "solutions": ["将农民口语化 Question 作为索引、专业农技 Answer 作为元数据", "强制收集关键条件后再进入 RAG 检索", "封装原生 Fetch 解析 SSE 并实现打字机渲染"],
        "tech_stack": ["FastAPI", "uni-app", "ChromaDB", "text2vec-base-chinese", "RAG", "SSE"],
        "links": [],
        "is_featured": True,
        "sort_order": 100,
    },
    {
        "slug": "agri-inventory-ledger",
        "title": "农资店进销存与智能账本系统",
        "subtitle": "覆盖 PC 管理端和移动端的轻量化全栈业务系统",
        "summary": "从零构建农资零售业务系统，后端基于 FastAPI，前端覆盖 PC 管理端和移动端，围绕库存、赊账、收银和部署维护完成高可用、低维护成本的业务闭环。",
        "project_type": "全栈业务系统",
        "background": "农资零售存在库存、赊账和收银链路割裂的问题，多人操作下容易出现超卖、欠款错乱和终端录入效率低。",
        "goals": "用低维护成本的全栈系统支撑进销存、赊账、收银和移动端查询，提升终端操作效率并保障账目一致性。",
        "role": "独立负责需求调研、数据库设计、FastAPI 接口、PC 管理端、uni-app 移动端、鉴权、事务处理和 Docker 部署。",
        "features": ["商品和库存管理", "赊账开单与欠款统计", "PC 管理端与移动端复用", "拼音首字母秒搜", "自定义抹零", "docker-compose 一键部署"],
        "challenges": ["库存扣减与欠款增加必须保持一致", "多用户并发下避免超卖", "终端收银需要极短操作路径", "服务器资源有限且维护成本要低"],
        "solutions": ["使用 MySQL 事务与 FOR UPDATE 悲观锁保障核心链路一致性", "反范式冗余当前欠款字段提升首页读取效率", "封装跨端请求拦截器与 HMAC-SHA256 签名鉴权", "使用 Docker 多阶段构建减少部署体积"],
        "tech_stack": ["Python", "FastAPI", "React", "Vue", "uni-app", "MySQL", "Docker"],
        "links": [],
        "is_featured": True,
        "sort_order": 90,
    },
    {
        "slug": "warehouse-3d-digital-twin",
        "title": "智能仓储 3D 可视化监控平台",
        "subtitle": "Three.js 数字孪生与 WCS 设备数据闭环",
        "summary": "面向千万级吞吐量智能仓储的数字孪生管控中枢，融合 WMS/WCS 业务数据与硬件状态，实现仓储场景 1:1 建模、堆垛机轨迹追踪和海量货位监控。",
        "project_type": "数字孪生 / 3D 可视化",
        "background": "智能仓储现场需要低延迟、高精度的大屏调度能力，传统二维看板难以直观呈现堆垛机、输送线和货位状态。",
        "goals": "构建稳定流畅的 3D 数字孪生大屏，让管理人员实时发现设备故障、通道拥堵和仓储运行异常。",
        "role": "前端核心开发，主导 3D 场景拆分、交互封装、性能优化，并使用 Python + MQTT 打通底层 WCS 设备数据。",
        "features": ["仓储场景 1:1 建模", "堆垛机实时轨迹追踪", "海量货位状态监控", "设备高亮与点选定位", "图表看板联动"],
        "challenges": ["上万个货位模型带来的内存和帧率压力", "高频设备状态刷新", "跨部门硬件数据联调周期长", "3D 交互逻辑需要可复用沉淀"],
        "solutions": ["使用 InstancedMesh 与 LOD 优化渲染性能", "通过 Python 数据网关订阅和清洗 MQTT 设备报文", "沉淀视角漫游、设备高亮、选点定位等 3D Hooks", "封装 ECharts 看板组件并统一状态管理"],
        "tech_stack": ["Vue3", "TypeScript", "Three.js", "ECharts", "Python", "FastAPI", "MQTT"],
        "links": [],
        "is_featured": True,
        "sort_order": 80,
    },
    {
        "slug": "interactive-ai-resume-rag",
        "title": "交互式 AI 履历系统 / 私有化 RAG 问答引擎",
        "subtitle": "基于个人履历知识库的本地化 RAG 对话体验",
        "summary": "以个人技术履历为切入场景，采用 Next.js + FastAPI + ChromaDB 打造私有化 RAG 知识库，通过 SSE 实现前后端流式输出，在限定知识边界内提供更准确、低幻觉的沉浸式问答体验。",
        "project_type": "AI / RAG 知识库",
        "background": "传统简历难以支持追问，单纯聊天 Demo 又缺少可信知识边界；项目用于验证本地化 RAG、Embedding 离线加载和流式交互的工程落地。",
        "goals": "将简历和项目经历结构化为可检索知识库，让访问者通过自然语言快速了解候选人的技术能力、项目深度和岗位匹配度。",
        "role": "独立全栈开发，负责产品定位、知识库构建、后端接口、SSE 流式响应、前端对话体验和 Docker 多服务编排。",
        "features": ["履历知识库问答", "本地 ChromaDB 向量检索", "SSE 打字机式流式输出", "多服务 Docker 编排", "限定知识边界的防幻觉回答"],
        "challenges": ["Embedding 模型离线加载", "RAG 知识边界控制", "前后端双线流式数据传输", "长文本响应导致的前端阻塞"],
        "solutions": ["采用本地 ChromaDB 管理向量数据", "用 FastAPI 统一封装检索与生成链路", "基于 SSE 协议渐进式渲染回答", "通过 Docker Compose 编排前端、后端和知识库服务"],
        "tech_stack": ["Next.js", "FastAPI", "ChromaDB", "RAG", "SSE", "Docker"],
        "links": [],
        "is_featured": True,
        "sort_order": 70,
    },
]

PROMPT_QUESTIONS = [
    ("请用 1 分钟介绍一下你的核心优势。", "positioning", 100),
    ("你适合 AI 全栈研发岗位的理由是什么？", "positioning", 90),
    ("讲讲脐橙农技 RAG Agent 如何降低大模型幻觉。", "project", 80),
    ("农资店进销存系统如何保证库存和赊账数据一致？", "engineering", 70),
    ("智能仓储 3D 可视化项目有哪些技术难点和业务价值？", "project", 60),
]

LEGACY_PROJECT_SLUGS = {
    "ai-resume-assistant",
    "portfolio-backend-api",
    "responsive-portfolio-ui",
}


def resume_source_path() -> Path:
    configured = os.getenv("SEED_RESUME_SOURCE")
    if configured:
        return Path(configured)
    return BACKEND_ROOT.parent / "卢官有-简历.pdf"


def upsert_project(db, data: dict) -> Project:
    project = db.scalar(select(Project).where(Project.slug == data["slug"]))
    if project is None:
        project = Project(**data, status="published")
        db.add(project)
    else:
        for key, value in data.items():
            setattr(project, key, value)
        project.status = "published"
        project.deleted_at = None
    db.flush()
    return project


def soft_delete_legacy_projects(db) -> None:
    desired_slugs = {project["slug"] for project in PROJECTS}
    legacy_slugs = LEGACY_PROJECT_SLUGS - desired_slugs
    if not legacy_slugs:
        return

    projects = db.scalars(select(Project).where(Project.slug.in_(legacy_slugs), Project.deleted_at.is_(None))).all()
    for project in projects:
        project.status = "hidden"
        project.is_featured = False
        project.deleted_at = utc_now()


def ensure_resume(db) -> None:
    upload_path = Path("uploads/resume/resume-current.pdf")
    source_path = resume_source_path()
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.exists() and source_path.resolve() != upload_path.resolve():
        shutil.copyfile(source_path, upload_path)

    resume_public_url = f"{settings.public_upload_base_url.rstrip('/')}/resume/resume-current.pdf"
    original_filename = source_path.name if source_path.exists() else "卢官有-简历.pdf"
    media = db.scalar(select(MediaAsset).where(MediaAsset.public_url == resume_public_url))
    if media is None:
        media = MediaAsset(
            media_type="document",
            purpose="resume",
            original_filename=original_filename,
            stored_filename="resume-current.pdf",
            storage_path=str(upload_path),
            public_url=resume_public_url,
            mime_type="application/pdf",
            file_ext="pdf",
            file_size=upload_path.stat().st_size if upload_path.exists() else 0,
            alt_text="卢官有当前简历 PDF",
            status="published",
        )
        db.add(media)
        db.flush()
    else:
        media.original_filename = original_filename
        media.storage_path = str(upload_path)
        media.file_size = upload_path.stat().st_size if upload_path.exists() else media.file_size
        media.alt_text = "卢官有当前简历 PDF"
        media.status = "published"
        media.deleted_at = None

    existing_current = db.scalars(select(ResumeFile).where(ResumeFile.is_current.is_(True))).all()
    for resume in existing_current:
        resume.is_current = False

    resume = db.scalar(select(ResumeFile).where(ResumeFile.media_id == media.id))
    if resume is None:
        resume = ResumeFile(
            title="卢官有-简历",
            media_id=media.id,
            version_label="2026",
            is_current=True,
            status="published",
        )
        db.add(resume)
    else:
        resume.title = "卢官有-简历"
        resume.version_label = "2026"
        resume.is_current = True
        resume.status = "published"
        resume.deleted_at = None


def ensure_site_profile(db) -> None:
    profile = db.scalar(select(SiteProfile).order_by(SiteProfile.id.asc()).limit(1))
    data = {
        "owner_name": "卢官有",
        "headline": "AI 驱动的全栈研发工程师 / 前端架构 / Python 后端 / RAG Agent",
        "summary": "5 年全栈研发经验，覆盖 Vue3、React、uni-app、Three.js 数字孪生、FastAPI、MySQL 与 Docker 部署。深度实践 Cursor 等 AI 编程工作流，能够从需求调研、数据库设计、前后端研发到上线部署完成闭环交付，并将 RAG、Agent、SSE 流式交互落地到真实业务系统。",
        "email": "923206295@qq.com",
        "phone": "18770919352",
        "wechat": "",
        "github_url": "",
        "portfolio_url": "",
        "extra_links": [],
        "status": "published",
    }
    if profile is None:
        db.add(SiteProfile(**data))
    else:
        for key, value in data.items():
            setattr(profile, key, value)


def ensure_prompt_questions(db) -> None:
    desired_questions = {question for question, _category, _sort_order in PROMPT_QUESTIONS}
    stale_questions = db.scalars(
        select(PromptQuestion).where(
            ~PromptQuestion.question.in_(desired_questions),
            PromptQuestion.deleted_at.is_(None),
        )
    ).all()
    for question in stale_questions:
        question.status = "hidden"
        question.deleted_at = utc_now()

    for question, category, sort_order in PROMPT_QUESTIONS:
        existing = db.scalar(select(PromptQuestion).where(PromptQuestion.question == question).order_by(PromptQuestion.id.asc()))
        if existing is None:
            db.add(
                PromptQuestion(
                    question=question,
                    category=category,
                    sort_order=sort_order,
                    status="published",
                )
            )
        else:
            existing.category = category
            existing.sort_order = sort_order
            existing.status = "published"
            existing.deleted_at = None


def ensure_admin(db) -> None:
    username = os.getenv("SEED_ADMIN_USERNAME", "admin")
    password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    admin = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if admin is None:
        db.add(
            AdminUser(
                username=username,
                password_hash=hash_password(password),
                display_name="卢官有",
                email="923206295@qq.com",
                status="active",
            )
        )
    else:
        admin.display_name = admin.display_name or "卢官有"
        admin.email = admin.email or "923206295@qq.com"
        admin.status = "active"
        admin.deleted_at = None
        if not verify_password(password, admin.password_hash):
            admin.password_hash = hash_password(password)


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        soft_delete_legacy_projects(db)
        for project_data in PROJECTS:
            upsert_project(db, project_data)
        ensure_resume(db)
        ensure_site_profile(db)
        ensure_prompt_questions(db)
        ensure_admin(db)
        db.commit()

    print("Seed data inserted. Admin username: admin")


def main() -> None:
    seed_database()


if __name__ == "__main__":
    main()
