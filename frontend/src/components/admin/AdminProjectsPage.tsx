import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'

import { adminService, type ProjectPayload } from '../../services/admin'
import type { AdminProject } from '../../services/types'
import {
  emptyProjectFormState,
  formStateToPayload,
  projectToFormState,
  type ProjectFormState,
} from './projectForm'
import { useAdminResource } from './useAdminResource'

type AdminPageProps = {
  token: string
}

type ProjectFormFieldsProps = {
  form: ProjectFormState
  onChange: (form: ProjectFormState) => void
}

function ProjectFormFields({ form, onChange }: ProjectFormFieldsProps) {
  function updateField<K extends keyof ProjectFormState>(field: K, value: ProjectFormState[K]) {
    onChange({ ...form, [field]: value })
  }

  return (
    <>
      <label>
        Slug
        <input value={form.slug} onChange={(event) => updateField('slug', event.target.value)} required />
      </label>
      <label>
        标题
        <input value={form.title} onChange={(event) => updateField('title', event.target.value)} required />
      </label>
      <label>
        副标题
        <input value={form.subtitle} onChange={(event) => updateField('subtitle', event.target.value)} />
      </label>
      <label>
        类型
        <input value={form.project_type} onChange={(event) => updateField('project_type', event.target.value)} required />
      </label>
      <label className="wide">
        摘要
        <textarea value={form.summary} onChange={(event) => updateField('summary', event.target.value)} required />
      </label>
      <label className="wide">
        项目背景
        <textarea value={form.background} onChange={(event) => updateField('background', event.target.value)} />
      </label>
      <label className="wide">
        项目目标
        <textarea value={form.goals} onChange={(event) => updateField('goals', event.target.value)} />
      </label>
      <label className="wide">
        我的职责
        <textarea value={form.role} onChange={(event) => updateField('role', event.target.value)} />
      </label>
      <label>
        技术栈（每行一个）
        <textarea
          value={form.tech_stack_text}
          onChange={(event) => updateField('tech_stack_text', event.target.value)}
          required
        />
      </label>
      <label>
        功能点（每行一个）
        <textarea value={form.features_text} onChange={(event) => updateField('features_text', event.target.value)} />
      </label>
      <label>
        技术难点（每行一个）
        <textarea value={form.challenges_text} onChange={(event) => updateField('challenges_text', event.target.value)} />
      </label>
      <label>
        解决方案（每行一个）
        <textarea value={form.solutions_text} onChange={(event) => updateField('solutions_text', event.target.value)} />
      </label>
      <label className="wide">
        相关链接（每行：标签 | URL | 类型）
        <textarea
          placeholder="GitHub | https://github.com/example/project | github"
          value={form.links_text}
          onChange={(event) => updateField('links_text', event.target.value)}
        />
      </label>
      <label>
        封面媒体 ID
        <input
          min="1"
          type="number"
          value={form.cover_media_id_text}
          onChange={(event) => updateField('cover_media_id_text', event.target.value)}
        />
      </label>
      <label>
        排序
        <input
          type="number"
          value={form.sort_order}
          onChange={(event) => updateField('sort_order', Number(event.target.value))}
        />
      </label>
      <label>
        状态
        <select value={form.status} onChange={(event) => updateField('status', event.target.value as ProjectPayload['status'])}>
          <option value="published">published</option>
          <option value="draft">draft</option>
          <option value="hidden">hidden</option>
        </select>
      </label>
      <label className="check-row">
        <input
          checked={form.is_featured}
          type="checkbox"
          onChange={(event) => updateField('is_featured', event.target.checked)}
        />
        精选项目
      </label>
    </>
  )
}

export function AdminProjectsPage({ token }: AdminPageProps) {
  const loader = useCallback(() => adminService.listProjects(token), [token])
  const { data: projects, loading, error, reload, setError } = useAdminResource<AdminProject[]>(loader, [])
  const [form, setForm] = useState<ProjectFormState>(emptyProjectFormState)
  const [editingProjectId, setEditingProjectId] = useState<number | null>(null)
  const [editForm, setEditForm] = useState<ProjectFormState>(emptyProjectFormState)
  const [saving, setSaving] = useState(false)
  const [savingEdit, setSavingEdit] = useState(false)

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await adminService.createProject(token, formStateToPayload(form))
      setForm(emptyProjectFormState)
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

  function startEditing(project: AdminProject) {
    setEditingProjectId(project.id)
    setEditForm(projectToFormState(project))
    setError('')
  }

  function cancelEditing() {
    setEditingProjectId(null)
    setEditForm(emptyProjectFormState)
  }

  async function saveProjectEdit(event: FormEvent<HTMLFormElement>, projectId: number) {
    event.preventDefault()
    setSavingEdit(true)
    setError('')
    try {
      await updateProject(projectId, formStateToPayload(editForm))
      cancelEditing()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : '保存失败')
    } finally {
      setSavingEdit(false)
    }
  }

  async function deleteProject(projectId: number) {
    await adminService.deleteProject(token, projectId)
    await reload()
  }

  return (
    <div className="admin-panel">
      <form className="admin-form admin-form-grid" onSubmit={(event) => void createProject(event)}>
        <ProjectFormFields form={form} onChange={setForm} />
        <div className="admin-form-actions wide">
          <button className="btn btn-primary" disabled={saving} type="submit">
            {saving ? '保存中...' : '新增项目'}
          </button>
        </div>
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
              <button className="btn btn-secondary" type="button" onClick={() => startEditing(project)}>
                {editingProjectId === project.id ? '编辑中' : '编辑'}
              </button>
              <button className="danger-button" type="button" onClick={() => void deleteProject(project.id)}>
                删除
              </button>
            </div>
            {editingProjectId === project.id ? (
              <form className="admin-form admin-form-grid project-edit-form" onSubmit={(event) => void saveProjectEdit(event, project.id)}>
                <ProjectFormFields form={editForm} onChange={setEditForm} />
                <div className="admin-form-actions wide">
                  <button className="btn btn-primary" disabled={savingEdit} type="submit">
                    {savingEdit ? '保存中...' : '保存修改'}
                  </button>
                  <button className="btn btn-secondary" disabled={savingEdit} type="button" onClick={cancelEditing}>
                    取消
                  </button>
                </div>
              </form>
            ) : null}
          </article>
        ))}
      </div>
    </div>
  )
}
