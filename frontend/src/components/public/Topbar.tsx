import type { SiteProfile } from '../../services/types'

type TopbarProps = {
  profile: SiteProfile
  resumeUrl: string
}

export function Topbar({ profile, resumeUrl }: TopbarProps) {
  const mark = profile.owner_name.slice(0, 1) || '卢'

  return (
    <header className="topbar">
      <div className="page-shell topbar-inner">
        <a href="#assistant" className="brand" aria-label="返回 AI 对话">
          <span className="brand-mark">{mark}</span>
          <span className="brand-copy">
            <span className="brand-name">{profile.owner_name}</span>
            <span className="brand-role">{profile.headline}</span>
          </span>
        </a>
        <nav className="nav" aria-label="主导航">
          <a href="#assistant">AI 对话</a>
          <a href="#projects">项目证据</a>
          <a href="#skills">能力</a>
          <a href="#contact">联系</a>
        </nav>
        <a className="nav-cta" href={resumeUrl}>
          下载简历
        </a>
      </div>
    </header>
  )
}
