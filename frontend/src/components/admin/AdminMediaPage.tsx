import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'

import { adminService } from '../../services/admin'
import type { AdminProject, MediaAsset } from '../../services/types'
import { useAdminResource } from './useAdminResource'

type AdminPageProps = {
  token: string
}

export function AdminMediaPage({ token }: AdminPageProps) {
  const mediaLoader = useCallback(() => adminService.listMedia(token), [token])
  const projectLoader = useCallback(() => adminService.listProjects(token), [token])
  const { data: media, loading, error, reload, setError } = useAdminResource<MediaAsset[]>(mediaLoader, [])
  const { data: projects } = useAdminResource<AdminProject[]>(projectLoader, [])
  const [mediaType, setMediaType] = useState<'image' | 'video' | 'document'>('image')
  const [purpose, setPurpose] = useState('screenshot')
  const [projectId, setProjectId] = useState('')
  const [altText, setAltText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file) {
      setError('请选择文件')
      return
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('media_type', mediaType)
    formData.append('purpose', purpose)
    formData.append('alt_text', altText)
    if (projectId) {
      formData.append('project_id', projectId)
    }

    setUploading(true)
    setError('')
    try {
      await adminService.uploadMedia(token, formData)
      setFile(null)
      setAltText('')
      await reload()
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : '上传失败')
    } finally {
      setUploading(false)
    }
  }

  async function updateMedia(mediaId: number, payload: Partial<MediaAsset>) {
    await adminService.updateMedia(token, mediaId, payload)
    await reload()
  }

  async function deleteMedia(mediaId: number) {
    await adminService.deleteMedia(token, mediaId)
    await reload()
  }

  return (
    <div className="admin-panel">
      <form className="admin-form admin-form-grid" onSubmit={(event) => void upload(event)}>
        <label>
          文件类型
          <select value={mediaType} onChange={(event) => setMediaType(event.target.value as typeof mediaType)}>
            <option value="image">image</option>
            <option value="video">video</option>
            <option value="document">document</option>
          </select>
        </label>
        <label>
          用途
          <input value={purpose} onChange={(event) => setPurpose(event.target.value)} />
        </label>
        <label>
          关联项目
          <select value={projectId} onChange={(event) => setProjectId(event.target.value)}>
            <option value="">不关联</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          说明
          <input value={altText} onChange={(event) => setAltText(event.target.value)} />
        </label>
        <label className="wide">
          文件
          <input type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        </label>
        <button className="btn btn-primary" disabled={uploading} type="submit">
          {uploading ? '上传中...' : '上传媒体'}
        </button>
      </form>

      {error ? <p className="inline-error">{error}</p> : null}
      {loading ? <p className="loading-line">正在加载媒体...</p> : null}

      <div className="admin-list media-list">
        {media.map((asset) => (
          <article className="admin-row media-row" key={asset.id}>
            <div className="media-thumb">
              {asset.media_type === 'image' && asset.url ? (
                <img src={asset.url} alt={asset.alt_text ?? asset.original_filename ?? '媒体预览'} />
              ) : (
                <span>{asset.media_type}</span>
              )}
            </div>
            <div>
              <strong>{asset.original_filename}</strong>
              <p>{asset.url}</p>
              <input
                aria-label="媒体说明"
                value={asset.alt_text ?? ''}
                onChange={(event) => void updateMedia(asset.id, { alt_text: event.target.value })}
              />
            </div>
            <div className="admin-row-actions">
              <select
                value={asset.status ?? 'published'}
                onChange={(event) => void updateMedia(asset.id, { status: event.target.value })}
              >
                <option value="published">published</option>
                <option value="draft">draft</option>
                <option value="hidden">hidden</option>
              </select>
              <button className="danger-button" type="button" onClick={() => void deleteMedia(asset.id)}>
                删除
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
