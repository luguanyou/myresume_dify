import fallbackHero from '../../assets/hero.png'
import type { ProjectListItem } from '../../services/types'

type ProjectGridProps = {
  projects: ProjectListItem[]
  loading: boolean
}

const fallbackProjects: ProjectListItem[] = [
  {
    id: 1,
    slug: 'ai-resume-assistant',
    title: 'AI 简历助手',
    subtitle: '可追问式简历体验',
    summary: '基于 Dify API 的可追问式简历体验，重点体现对话 UI、SSE 流式渲染、后端代理和项目证据组织。',
    project_type: 'AI 应用',
    role: '前端、后端 API、Dify 代理和响应式体验',
    tech_stack: ['React', 'Python', 'Dify', 'SSE'],
    cover_media: null,
    is_featured: true,
    sort_order: 100,
  },
  {
    id: 2,
    slug: 'portfolio-backend-api',
    title: 'Portfolio Backend API',
    subtitle: '作品集内容 API',
    summary: 'FastAPI + SQLAlchemy 管理项目、媒体、简历和预设问题，并通过 Bearer token 保护后台接口。',
    project_type: '后端',
    role: '接口设计、数据建模、测试覆盖',
    tech_stack: ['FastAPI', 'SQLAlchemy', 'MySQL'],
    cover_media: null,
    is_featured: true,
    sort_order: 90,
  },
  {
    id: 3,
    slug: 'responsive-portfolio-ui',
    title: '响应式作品集前台',
    subtitle: '移动端优先展示 AI 对话',
    summary: '手机端优先保留 AI 对话入口，让招聘方在微信或浏览器中打开时，也能直接提问并查看关键材料。',
    project_type: '前端',
    role: 'React 组件拆分、视觉迁移、移动端适配',
    tech_stack: ['React', 'Vite', 'TypeScript'],
    cover_media: null,
    is_featured: true,
    sort_order: 80,
  },
]

function projectImage(project: ProjectListItem) {
  return project.cover_media?.url || fallbackHero
}

export function ProjectGrid({ projects, loading }: ProjectGridProps) {
  const visibleProjects = projects.length > 0 ? projects : fallbackProjects

  return (
    <section className="page-shell section" id="projects">
      <div className="section-head">
        <div>
          <p className="eyebrow">项目证据</p>
          <h2>不是只写关键词，而是让面试官能看到作品。</h2>
        </div>
        <p className="section-note">
          ProjectGrid 接入 /api/projects?featured=true。AI 对话给入口，项目材料负责增强可信度。
        </p>
      </div>

      {loading ? <p className="loading-line">正在加载精选项目...</p> : null}

      <div className="project-grid">
        {visibleProjects.map((project) => (
          <article className="project-card" key={project.id}>
            <div className="project-media">
              <img src={projectImage(project)} alt={`${project.title} 截图`} />
              <span className="media-chip">{project.is_featured ? '精选项目' : '项目'}</span>
            </div>
            <div className="project-content">
              <div className="project-title-row">
                <h3>{project.title}</h3>
                <span className="project-type">{project.project_type}</span>
              </div>
              {project.subtitle ? <strong className="project-subtitle">{project.subtitle}</strong> : null}
              <p>{project.summary}</p>
              <div className="stack">
                {project.tech_stack.slice(0, 5).map((tech) => (
                  <span key={tech}>{tech}</span>
                ))}
              </div>
              <a className="detail-link" href="#assistant">
                向 AI 追问详情 →
              </a>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
