import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'

import { adminService } from '../../services/admin'
import type { AdminResume } from '../../services/types'
import { useAdminResource } from './useAdminResource'

type AdminPageProps = {
  token: string
}

export function AdminResumesPage({ token }: AdminPageProps) {
  const loader = useCallback(() => adminService.listResumes(token), [token])
  const { data: resumes, loading, error, reload, setError } = useAdminResource<AdminResume[]>(loader, [])
  const [title, setTitle] = useState('当前简历')
  const [version, setVersion] = useState('')
  const [setCurrent, setSetCurrent] = useState(true)
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file) {
      setError('请选择 PDF 文件')
      return
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('version_label', version)
    formData.append('set_current', String(setCurrent))

    setUploading(true)
    setError('')
    try {
      await adminService.uploadResume(token, formData)
      setFile(null)
      await reload()
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : '上传失败')
    } finally {
      setUploading(false)
    }
  }

  async function markCurrent(resumeId: number) {
    await adminService.setCurrentResume(token, resumeId)
    await reload()
  }

  return (
    <div className="admin-panel">
      <form className="admin-form admin-form-grid" onSubmit={(event) => void upload(event)}>
        <label>
          标题
          <input value={title} onChange={(event) => setTitle(event.target.value)} required />
        </label>
        <label>
          版本
          <input value={version} onChange={(event) => setVersion(event.target.value)} />
        </label>
        <label className="check-row">
          <input checked={setCurrent} type="checkbox" onChange={(event) => setSetCurrent(event.target.checked)} />
          上传后设为当前简历
        </label>
        <label className="wide">
          PDF 文件
          <input accept="application/pdf" type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        </label>
        <button className="btn btn-primary" disabled={uploading} type="submit">
          {uploading ? '上传中...' : '上传简历'}
        </button>
      </form>

      {error ? <p className="inline-error">{error}</p> : null}
      {loading ? <p className="loading-line">正在加载简历...</p> : null}

      <div className="admin-list">
        {resumes.map((resume) => (
          <article className="admin-row" key={resume.id}>
            <div>
              <strong>{resume.title}</strong>
              <p>
                {resume.version_label || '无版本标记'} · {resume.status}
                {resume.is_current ? ' · 当前版本' : ''}
              </p>
            </div>
            <div className="admin-row-actions">
              {resume.is_current ? (
                <a className="btn btn-secondary" href="/api/resume/download">
                  下载当前
                </a>
              ) : (
                <button className="btn btn-secondary" type="button" onClick={() => void markCurrent(resume.id)}>
                  设为当前
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
