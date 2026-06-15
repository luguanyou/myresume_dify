import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'

import { adminService } from '../../services/admin'
import type { AdminUser } from '../../services/types'
import { AdminDashboard } from './AdminDashboard'
import { AdminLogin } from './AdminLogin'

const tokenKey = 'portfolioAdminToken'

export function AdminApp() {
  const [token, setToken] = useState(() => window.localStorage.getItem(tokenKey) ?? '')
  const [admin, setAdmin] = useState<AdminUser | null>(null)
  const [checking, setChecking] = useState(Boolean(token))
  const [loginError, setLoginError] = useState('')

  useEffect(() => {
    if (!token) {
      return
    }

    let mounted = true
    adminService
      .me(token)
      .then((user) => {
        if (mounted) {
          setAdmin(user)
          setLoginError('')
        }
      })
      .catch(() => {
        if (mounted) {
          window.localStorage.removeItem(tokenKey)
          setToken('')
          setAdmin(null)
        }
      })
      .finally(() => {
        if (mounted) {
          setChecking(false)
        }
      })

    return () => {
      mounted = false
    }
  }, [token])

  function clearSession() {
    window.localStorage.removeItem(tokenKey)
    setToken('')
    setAdmin(null)
    setChecking(false)
  }

  async function handleLogin(username: string, password: string) {
    setLoginError('')
    const login = await adminService.login(username, password)
    window.localStorage.setItem(tokenKey, login.access_token)
    setToken(login.access_token)
    setAdmin(login.admin)
  }

  async function handleLogout() {
    if (token) {
      await adminService.logout(token).catch(() => undefined)
    }
    clearSession()
  }

  const loginSubmit = useMemo(
    () => async (event: FormEvent<HTMLFormElement>, username: string, password: string) => {
      event.preventDefault()
      try {
        await handleLogin(username, password)
      } catch (error) {
        setLoginError(error instanceof Error ? error.message : '登录失败')
      }
    },
    [],
  )

  if (checking) {
    return (
      <main className="admin-loading">
        <span className="admin-logo">卢</span>
        <p>正在校验管理员身份...</p>
      </main>
    )
  }

  if (!token || !admin) {
    return <AdminLogin error={loginError} onSubmit={loginSubmit} />
  }

  return <AdminDashboard admin={admin} token={token} onLogout={() => void handleLogout()} />
}
