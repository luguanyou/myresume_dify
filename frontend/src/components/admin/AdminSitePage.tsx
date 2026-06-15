import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'

import { adminService, type SiteProfilePayload } from '../../services/admin'
import type { SiteProfile } from '../../services/types'
import { useAdminResource } from './useAdminResource'

type AdminPageProps = {
  token: string
}

const emptyProfile: SiteProfilePayload = {
  owner_name: '',
  headline: '',
  summary: '',
  email: '',
  phone: '',
  wechat: '',
  github_url: '',
  portfolio_url: '',
  extra_links: [],
  status: 'published',
}

export function AdminSitePage({ token }: AdminPageProps) {
  const loader = useCallback(() => adminService.getSiteProfile(token), [token])
  const { data: profile, loading, error, reload, setError } = useAdminResource<SiteProfile>(loader, emptyProfile)
  const [form, setForm] = useState<SiteProfilePayload | null>(null)
  const [saving, setSaving] = useState(false)

  const activeForm = form ?? {
      ...emptyProfile,
      ...profile,
      owner_name: profile.owner_name ?? '',
      headline: profile.headline ?? '',
      status: profile.status ?? 'published',
    }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await adminService.updateSiteProfile(token, activeForm)
      await reload()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="admin-panel">
      <form className="admin-form admin-form-grid" onSubmit={(event) => void save(event)}>
        <label>
          姓名
          <input
            value={activeForm.owner_name}
            onChange={(event) => setForm({ ...activeForm, owner_name: event.target.value })}
            required
          />
        </label>
        <label>
          标题
          <input
            value={activeForm.headline}
            onChange={(event) => setForm({ ...activeForm, headline: event.target.value })}
            required
          />
        </label>
        <label>
          邮箱
          <input value={activeForm.email ?? ''} onChange={(event) => setForm({ ...activeForm, email: event.target.value })} />
        </label>
        <label>
          电话
          <input value={activeForm.phone ?? ''} onChange={(event) => setForm({ ...activeForm, phone: event.target.value })} />
        </label>
        <label>
          微信
          <input value={activeForm.wechat ?? ''} onChange={(event) => setForm({ ...activeForm, wechat: event.target.value })} />
        </label>
        <label>
          GitHub
          <input
            value={activeForm.github_url ?? ''}
            onChange={(event) => setForm({ ...activeForm, github_url: event.target.value })}
          />
        </label>
        <label>
          作品集 URL
          <input
            value={activeForm.portfolio_url ?? ''}
            onChange={(event) => setForm({ ...activeForm, portfolio_url: event.target.value })}
          />
        </label>
        <label>
          状态
          <select
            value={activeForm.status}
            onChange={(event) => setForm({ ...activeForm, status: event.target.value as 'published' | 'hidden' })}
          >
            <option value="published">published</option>
            <option value="hidden">hidden</option>
          </select>
        </label>
        <label className="wide">
          简介
          <textarea
            value={activeForm.summary ?? ''}
            onChange={(event) => setForm({ ...activeForm, summary: event.target.value })}
          />
        </label>
        <button className="btn btn-primary" disabled={saving} type="submit">
          {saving ? '保存中...' : '保存站点设置'}
        </button>
      </form>

      {loading ? <p className="loading-line">正在加载站点设置...</p> : null}
      {error ? <p className="inline-error">{error}</p> : null}
    </div>
  )
}
