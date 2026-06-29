import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import fallbackHero from '../../assets/hero.png'
import { portfolioHomePath } from '../../routes'
import { projectService } from '../../services/projects'
import { resumeDownloadUrl } from '../../services/public'
import type { MediaAsset, ProjectDetail } from '../../services/types'

type ProjectDetailPageProps = {
  projectId: number
}

type ProjectDetailState = {
  project: ProjectDetail | null
  loading: boolean
  error: string
}

function cleanItems(items: string[] | undefined) {
  return (items ?? []).map((item) => item.trim()).filter(Boolean)
}

function firstImageMedia(project: ProjectDetail) {
  return project.media.find((item) => item.url && item.media_type.toLowerCase().includes('image'))
}

function projectCover(project: ProjectDetail) {
  return project.cover_media?.url || firstImageMedia(project)?.url || fallbackHero
}

function sectionId(title: string) {
  return title.toLowerCase().replace(/\s+/g, '-')
}

function DetailSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="detail-section" aria-labelledby={sectionId(title)}>
      <p className="eyebrow">{title}</p>
      <div id={sectionId(title)}>{children}</div>
    </section>
  )
}

function TextSection({ title, body }: { title: string; body?: string | null }) {
  if (!body?.trim()) {
    return null
  }

  return (
    <DetailSection title={title}>
      <p>{body}</p>
    </DetailSection>
  )
}

function ListSection({ title, items }: { title: string; items: string[] }) {
  const visibleItems = cleanItems(items)
  if (visibleItems.length === 0) {
    return null
  }

  return (
    <DetailSection title={title}>
      <ul className="detail-list">
        {visibleItems.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </DetailSection>
  )
}

function mediaLabel(media: MediaAsset) {
  return media.alt_text || media.original_filename || media.purpose || '项目材料'
}

function isImage(media: MediaAsset) {
  return media.media_type.toLowerCase().includes('image')
}

function isVideo(media: MediaAsset) {
  return media.media_type.toLowerCase().includes('video')
}

function MediaEvidence({ media }: { media: MediaAsset }) {
  if (!media.url) {
    return null
  }

  return (
    <figure className="media-evidence-card">
      <div className="media-evidence-preview">
        {isImage(media) ? <img src={media.url} alt={mediaLabel(media)} /> : null}
        {isVideo(media) ? <video src={media.url} controls preload="metadata" aria-label={mediaLabel(media)} /> : null}
        {!isImage(media) && !isVideo(media) ? (
          <a className="media-file-link" href={media.url} target="_blank" rel="noreferrer">
            查看文件
          </a>
        ) : null}
      </div>
      <figcaption>
        <strong>{mediaLabel(media)}</strong>
        {media.purpose ? <span>{media.purpose}</span> : null}
      </figcaption>
    </figure>
  )
}

export function ProjectDetailPage({ projectId }: ProjectDetailPageProps) {
  const [state, setState] = useState<ProjectDetailState>({
    project: null,
    loading: true,
    error: '',
  })

  useEffect(() => {
    let mounted = true

    async function loadProject() {
      setState({ project: null, loading: true, error: '' })
      try {
        const project = await projectService.getProjectDetail(projectId)
        if (mounted) {
          setState({ project, loading: false, error: '' })
        }
      } catch (error) {
        if (mounted) {
          setState({
            project: null,
            loading: false,
            error: error instanceof Error ? error.message : '项目详情暂时无法加载',
          })
        }
      }
    }

    void loadProject()

    return () => {
      mounted = false
    }
  }, [projectId])

  const homePath = portfolioHomePath()
  const media = useMemo(() => state.project?.media.filter((item) => item.url) ?? [], [state.project])

  if (state.loading) {
    return (
      <main className="detail-page">
        <section className="page-shell detail-state" role="status">
          正在加载项目详情...
        </section>
      </main>
    )
  }

  if (state.error || !state.project) {
    return (
      <main className="detail-page">
        <section className="page-shell detail-state detail-error" role="alert">
          <p>{state.error || '没有找到这个项目。'}</p>
          <a className="btn btn-primary" href={homePath}>
            返回作品集
          </a>
        </section>
      </main>
    )
  }

  const project = state.project
  const projectLinks = project.links.filter((link) => link.url)
  const techStack = cleanItems(project.tech_stack)

  return (
    <div className="detail-page">
      <header className="detail-topbar">
        <div className="page-shell detail-topbar-inner">
          <a className="brand" href={homePath} aria-label="返回作品集首页">
            <span className="brand-mark">项</span>
            <span className="brand-copy">
              <span className="brand-name">项目详情</span>
              <span className="brand-role">返回作品集继续查看简历与能力证据</span>
            </span>
          </a>
          <div className="detail-topbar-actions">
            <a className="btn btn-secondary" href={homePath}>
              返回首页
            </a>
            <a className="nav-cta" href={resumeDownloadUrl}>
              下载简历
            </a>
          </div>
        </div>
      </header>

      <main>
        <section className="page-shell project-detail-hero">
          <div className="project-detail-copy">
            <p className="eyebrow">{project.project_type}</p>
            <h1>{project.title}</h1>
            {project.subtitle ? <strong className="project-detail-subtitle">{project.subtitle}</strong> : null}
            <p className="project-detail-summary">{project.summary}</p>
            {techStack.length > 0 ? (
              <div className="stack" aria-label="技术栈">
                {techStack.map((tech) => (
                  <span key={tech}>{tech}</span>
                ))}
              </div>
            ) : null}
          </div>
          <div className="project-detail-cover">
            <img src={projectCover(project)} alt={`${project.title} 项目封面`} />
          </div>
        </section>

        <section className="page-shell project-detail-layout">
          <aside className="detail-side-panel" aria-label="项目概览">
            <div>
              <p className="panel-title">我的职责</p>
              <p>{project.role || '项目职责暂未填写。'}</p>
            </div>
            <div>
              <p className="panel-title">项目类型</p>
              <p>{project.project_type}</p>
            </div>
            {projectLinks.length > 0 ? (
              <div>
                <p className="panel-title">相关链接</p>
                <div className="detail-link-list">
                  {projectLinks.map((link) => (
                    <a href={link.url} key={`${link.label}-${link.url}`} target="_blank" rel="noreferrer">
                      {link.label || link.link_type || '查看链接'}
                    </a>
                  ))}
                </div>
              </div>
            ) : null}
          </aside>

          <div className="detail-main">
            <TextSection title="项目背景" body={project.background} />
            <TextSection title="项目目标" body={project.goals} />
            <ListSection title="核心功能" items={project.features} />
            <ListSection title="技术挑战" items={project.challenges} />
            <ListSection title="解决方案" items={project.solutions} />
          </div>
        </section>

        {media.length > 0 ? (
          <section className="page-shell detail-media-section">
            <div className="section-head">
              <div>
                <p className="eyebrow">项目证据</p>
                <h2>截图、视频和文档材料</h2>
              </div>
            </div>
            <div className="media-evidence-grid">
              {media.map((item) => (
                <MediaEvidence media={item} key={item.id} />
              ))}
            </div>
          </section>
        ) : null}
      </main>
    </div>
  )
}

