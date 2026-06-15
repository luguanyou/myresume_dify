import { useEffect, useMemo, useState } from 'react'

import { projectService } from '../../services/projects'
import { publicService, resumeDownloadUrl } from '../../services/public'
import type { ProjectListItem, PromptQuestion, Resume, SiteProfile } from '../../services/types'
import { CandidateSummary } from './CandidateSummary'
import { ChatPanel } from './ChatPanel'
import { ContactBand } from './ContactBand'
import { ProjectGrid } from './ProjectGrid'
import { SkillSections } from './SkillSections'
import { Topbar } from './Topbar'

type PublicState = {
  profile: SiteProfile | null
  prompts: PromptQuestion[]
  projects: ProjectListItem[]
  resume: Resume | null
  loading: boolean
  error: string
}

const fallbackProfile: SiteProfile = {
  owner_name: '卢官有',
  headline: 'AI 应用开发 / 前端工程 / Python 后端',
  summary:
    '我把传统简历改成可追问的 AI 对话入口，同时保留项目截图、视频和职责说明。面试官不用先翻长 PDF，可以直接问：做过什么、负责哪部分、难点怎么解决。',
  email: '',
  github_url: '',
  portfolio_url: '',
  extra_links: [],
}

const fallbackPrompts: PromptQuestion[] = [
  { id: 1, question: '你最适合什么岗位？为什么？', category: 'positioning', sort_order: 100 },
  { id: 2, question: 'Dify 简历助手你负责了哪部分？', category: 'project', sort_order: 90 },
  { id: 3, question: '有哪些可以验证的项目截图或视频？', category: 'proof', sort_order: 80 },
  { id: 4, question: '前端、后端和 AI 应用能力分别体现在哪？', category: 'skills', sort_order: 70 },
  { id: 5, question: '如果接手业务型 AI Agent，你会怎么落地？', category: 'agent', sort_order: 60 },
]

function normalizeProfile(profile: SiteProfile | null) {
  return {
    ...fallbackProfile,
    ...profile,
    owner_name: profile?.owner_name || fallbackProfile.owner_name,
    headline: profile?.headline || fallbackProfile.headline,
    summary: profile?.summary || fallbackProfile.summary,
  }
}

export function PortfolioPage() {
  const [state, setState] = useState<PublicState>({
    profile: null,
    prompts: [],
    projects: [],
    resume: null,
    loading: true,
    error: '',
  })

  useEffect(() => {
    let mounted = true

    async function loadPublicData() {
      try {
        const [profile, prompts, projects, resume] = await Promise.all([
          publicService.getSiteProfile(),
          publicService.getPromptQuestions(),
          projectService.getFeaturedProjects(),
          publicService.getCurrentResume().catch(() => null),
        ])

        if (!mounted) {
          return
        }

        setState({
          profile,
          prompts,
          projects,
          resume,
          loading: false,
          error: '',
        })
      } catch (error) {
        if (!mounted) {
          return
        }

        setState((current) => ({
          ...current,
          loading: false,
          error: error instanceof Error ? error.message : '公开内容暂时无法加载',
        }))
      }
    }

    loadPublicData()

    return () => {
      mounted = false
    }
  }, [])

  const profile = useMemo(() => normalizeProfile(state.profile), [state.profile])
  const prompts = state.prompts.length > 0 ? state.prompts : fallbackPrompts

  return (
    <>
      <Topbar profile={profile} resumeUrl={resumeDownloadUrl} />
      <main>
        <section className="page-shell hero">
          <ChatPanel prompts={prompts} />
          <CandidateSummary profile={profile} resume={state.resume} resumeUrl={resumeDownloadUrl} />
        </section>

        {state.error ? (
          <section className="page-shell notice" role="status">
            {state.error}，页面已使用本地展示内容继续渲染。
          </section>
        ) : null}

        <ProjectGrid projects={state.projects} loading={state.loading} />
        <SkillSections />
        <ContactBand profile={profile} resumeUrl={resumeDownloadUrl} />
      </main>
      <footer className="page-shell footer">
        <span>© 2026 {profile.owner_name} · AI 简历对话作品集 · React / Python / Dify / SSE</span>
      </footer>
    </>
  )
}
