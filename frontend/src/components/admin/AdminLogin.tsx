import { useState } from 'react'
import type { FormEvent } from 'react'

type AdminLoginProps = {
  error: string
  onSubmit: (event: FormEvent<HTMLFormElement>, username: string, password: string) => Promise<void>
}

export function AdminLogin({ error, onSubmit }: AdminLoginProps) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    setSubmitting(true)
    await onSubmit(event, username, password).finally(() => setSubmitting(false))
  }

  return (
    <main className="admin-auth-page">
      <section className="admin-login-card">
        <span className="admin-logo">卢</span>
        <p className="eyebrow">后台管理</p>
        <h1>登录后维护作品集内容</h1>
        <form className="admin-form" onSubmit={(event) => void handleSubmit(event)}>
          <label>
            账号
            <input value={username} onChange={(event) => setUsername(event.target.value)} />
          </label>
          <label>
            密码
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
          {error ? <p className="inline-error">{error}</p> : null}
          <button className="btn btn-primary" disabled={submitting} type="submit">
            {submitting ? '登录中...' : '登录'}
          </button>
        </form>
      </section>
    </main>
  )
}
