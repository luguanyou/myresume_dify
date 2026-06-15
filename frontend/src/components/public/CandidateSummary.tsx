import type { Resume, SiteProfile } from '../../services/types'

type CandidateSummaryProps = {
  profile: SiteProfile
  resume: Resume | null
  resumeUrl: string
}

export function CandidateSummary({ profile, resume, resumeUrl }: CandidateSummaryProps) {
  const skills = ['React', 'Python', 'Dify', 'SSE 流式响应', 'AI Agent', 'MySQL', 'Three.js']

  return (
    <aside className="candidate-panel" aria-label="候选人摘要">
      <section className="candidate-card">
        <span className="candidate-kicker">
          <span className="status-dot"></span>打开页面即可提问
        </span>
        <h1>{profile.owner_name}</h1>
        <p className="candidate-title">{profile.headline}</p>
        <p className="candidate-summary">{profile.summary}</p>
        <div className="action-row">
          <a className="btn btn-primary" href="#assistant">
            开始提问
          </a>
          <a className="btn btn-secondary" href={resume?.download_url ?? resumeUrl}>
            下载 PDF
          </a>
        </div>
      </section>

      <section className="evidence-panel" aria-label="可验证材料">
        <div className="panel-block">
          <p className="panel-title">可验证材料</p>
          <div className="evidence-list">
            <a className="evidence-item" href="#projects">
              <span className="evidence-icon">图</span>
              <span>项目截图、媒体资源和项目职责说明集中在项目证据区。</span>
            </a>
            <a className="evidence-item" href="#assistant">
              <span className="evidence-icon">问</span>
              <span>AI 对话支持追问岗位匹配、项目细节、技术边界和落地路径。</span>
            </a>
            <a className="evidence-item" href="#skills">
              <span className="evidence-icon">栈</span>
              <span>能力范围按前端、后端、AI 应用和交付拆分，便于快速扫描。</span>
            </a>
          </div>
        </div>
        <div className="panel-block">
          <p className="panel-title">重点技术</p>
          <div className="tag-cloud">
            {skills.map((skill) => (
              <span
                className={`tag ${skill === 'Dify' ? 'accent' : ''} ${skill === 'AI Agent' ? 'signal' : ''}`}
                key={skill}
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </section>
    </aside>
  )
}
