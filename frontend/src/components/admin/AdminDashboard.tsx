import { useState } from 'react'

import type { AdminUser } from '../../services/types'
import { AdminMediaPage } from './AdminMediaPage'
import { AdminProjectsPage } from './AdminProjectsPage'
import { AdminPromptQuestionsPage } from './AdminPromptQuestionsPage'
import { AdminResumesPage } from './AdminResumesPage'
import { AdminSitePage } from './AdminSitePage'

type AdminDashboardProps = {
  admin: AdminUser
  token: string
  onLogout: () => void
}

type AdminTab = 'projects' | 'media' | 'resumes' | 'site' | 'prompts'

const tabs: Array<{ id: AdminTab; label: string }> = [
  { id: 'projects', label: '项目管理' },
  { id: 'media', label: '媒体管理' },
  { id: 'resumes', label: '简历管理' },
  { id: 'site', label: '站点设置' },
  { id: 'prompts', label: '预设问题' },
]

const appBasePath = import.meta.env.BASE_URL || '/'

export function AdminDashboard({ admin, token, onLogout }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<AdminTab>('projects')

  return (
    <main className="admin-shell">
      <aside className="admin-sidebar">
        <a className="admin-brand" href={appBasePath}>
          <span className="admin-logo">卢</span>
          <span>
            <strong>Portfolio Admin</strong>
            <small>{admin.display_name || admin.username}</small>
          </span>
        </a>
        <nav className="admin-tabs" aria-label="后台导航">
          {tabs.map((tab) => (
            <button
              className={activeTab === tab.id ? 'active' : ''}
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <button className="admin-logout" type="button" onClick={onLogout}>
          退出登录
        </button>
      </aside>

      <section className="admin-main">
        <header className="admin-header">
          <div>
            <p className="eyebrow">Authorization Bearer token 已启用</p>
            <h1>{tabs.find((tab) => tab.id === activeTab)?.label}</h1>
          </div>
          <a className="btn btn-secondary" href={appBasePath}>
            查看前台
          </a>
        </header>

        {activeTab === 'projects' ? <AdminProjectsPage token={token} /> : null}
        {activeTab === 'media' ? <AdminMediaPage token={token} /> : null}
        {activeTab === 'resumes' ? <AdminResumesPage token={token} /> : null}
        {activeTab === 'site' ? <AdminSitePage token={token} /> : null}
        {activeTab === 'prompts' ? <AdminPromptQuestionsPage token={token} /> : null}
      </section>
    </main>
  )
}
