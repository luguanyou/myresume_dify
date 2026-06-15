import type { SiteProfile } from '../../services/types'

type ContactBandProps = {
  profile: SiteProfile
  resumeUrl: string
}

export function ContactBand({ profile, resumeUrl }: ContactBandProps) {
  return (
    <section className="page-shell" id="contact">
      <div className="contact-band">
        <div>
          <h2>想继续了解，可以直接问，也可以下载简历。</h2>
          <p>
            这个作品集的重点是把“简历阅读”变成“可追问的面试入口”：AI 对话负责快速解释，项目证据负责证明经历真实。
            {profile.email ? ` 也可以通过 ${profile.email} 联系。` : ''}
          </p>
        </div>
        <div className="contact-actions">
          <a className="btn btn-primary" href="#assistant">
            回到 AI 对话
          </a>
          <a className="btn btn-secondary" href={resumeUrl}>
            下载简历
          </a>
        </div>
      </div>
    </section>
  )
}
