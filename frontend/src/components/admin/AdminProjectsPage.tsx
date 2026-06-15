import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'

import { adminService, type ProjectPayload } from '../../services/admin'
import type { AdminProject } from '../../services/types'
import { useAdminResource } from './useAdminResource'

type AdminPageProps = {
  token: string
}

const emptyProject: ProjectPayload = {
  slug: '',
  title: '',
  subtitle: '',
  summary: '',
  project_type: 'AI 应用',
  background: '',
  goals: '',
  role: '',
  features: [],
  challenges: [],
  solutions: [],
  tech_stack: [],
  links: [],
  cover_media_id: null,
  status: 'published',
  is_featured: true,
  sort_order: 0,
}

function linesToArray(value: string) {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

export function AdminProjectsPage({ token }: AdminPageProps) {
  const loader = useCallback(() => adminService.listProjects(token), [token])
  const { data: projects, loading, error, reload, setError } = useAdminResource<AdminProject[]>(loader, [])
  const [form, setForm] = useState({
    ...emptyProject,
    tech_stack_text: '',
    features_text: '',
    challenges_text: '',
    solutions_text: '',
  })
  const [saving, setSaving] = useState(false)

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await adminService.createProject(token, {
        slug: form.slug,
        title: form.title,
        subtitle: form.subtitle,
        summary: form.summary,
        project_type: form.project_type,
        background: form.background,
        goals: form.goals,
        role: form.role,
        tech_stack: linesToArray(form.tech_stack_text),
        features: linesToArray(form.features_text),
        challenges: linesToArray(form.challenges_text),
        solutions: linesToArray(form.solutions_text),
        links: [],
        cover_media_id: form.cover_media_id,
        status: form.status,
        is_featured: form.is_featured,
        sort_order: form.sort_order,
      })
      setForm({ ...emptyProject, tech_stack_text: '', features_text: '', challenges_text: '', solutions_text: '' })
      await reload()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  async function updateProject(projectId: number, payload: Partial<ProjectPayload>) {
    await adminService.updateProject(token, projectId, payload)
    await reload()
  }

  async function deleteProject(projectId: number) {
    await adminService.deleteProject(token, projectId)
    await reload()
  }

  return (
    <div className="admin-panel">
      <form className="admin-form admin-form-grid" onSubmit={(event) => void createProject(event)}>
        <label>
          Slug
          <input value={form.slug} onChange={(event) => setForm({ ...form, slug: event.target.value })} required />
        </label>
        <label>
          标题
          <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
        </label>
        <label>
          副标题
          <input value={form.subtitle ?? ''} onChange={(event) => setForm({ ...form, subtitle: event.target.value })} />
        </label>
        <label>
          类型
          <input
            value={form.project_type}
            onChange={(event) => setForm({ ...form, project_type: event.target.value })}
            required
          />
        </label>
        <label className="wide">
          摘要
          <textarea
            value={form.summary}
            onChange={(event) => setForm({ ...form, summary: event.target.value })}
            required
          />
        </label>
        <label>
          技术栈（每行一个）
          <textarea
            value={form.tech_stack_text}
            onChange={(event) => setForm({ ...form, tech_stack_text: event.target.value })}
            required
          />
        </label>
        <label>
          功能点（每行一个）
          <textarea value={form.features_text} onChange={(event) => setForm({ ...form, features_text: event.target.value })} />
        </label>
        <label>
          排序
          <input
            type="number"
            value={form.sort_order}
            onChange={(event) => setForm({ ...form, sort_order: Number(event.target.value) })}
          />
        </label>
        <label>
          状态
          <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as ProjectPayload['status'] })}>
            <option value="published">published</option>
            <option value="draft">draft</option>
            <option value="hidden">hidden</option>
          </select>
        </label>
        <label className="check-row">
          <input
            checked={form.is_featured}
            type="checkbox"
            onChange={(event) => setForm({ ...form, is_featured: event.target.checked })}
          />
          精选项目
        </label>
        <button className="btn btn-primary" disabled={saving} type="submit">
          {saving ? '保存中...' : '新增项目'}
        </button>
      </form>

      {error ? <p className="inline-error">{error}</p> : null}
      {loading ? <p className="loading-line">正在加载项目...</p> : null}

      <div className="admin-list">
        {projects.map((project) => (
          <article className="admin-row" key={project.id}>
            <div>
              <strong>{project.title}</strong>
              <p>{project.summary}</p>
              <div className="stack">
                {project.tech_stack.map((tech) => (
                  <span key={tech}>{tech}</span>
                ))}
              </div>
            </div>
            <div className="admin-row-actions">
              <select
                value={project.status}
                onChange={(event) => void updateProject(project.id, { status: event.target.value as ProjectPayload['status'] })}
              >
                <option value="published">published</option>
                <option value="draft">draft</option>
                <option value="hidden">hidden</option>
              </select>
              <label className="compact-check">
                <input
                  checked={project.is_featured}
                  type="checkbox"
                  onChange={(event) => void updateProject(project.id, { is_featured: event.target.checked })}
                />
                精选
              </label>
              <input
                aria-label={`${project.title} 排序`}
                type="number"
                value={project.sort_order}
                onChange={(event) => void updateProject(project.id, { sort_order: Number(event.target.value) })}
              />
              <button className="danger-button" type="button" onClick={() => void deleteProject(project.id)}>
                删除
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
