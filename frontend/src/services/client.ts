import type { ApiEnvelope, ApiErrorEnvelope } from './types'

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '/dify/api'

export class ApiError extends Error {
  code: string
  status: number

  constructor(message: string, code: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

function buildUrl(path: string) {
  if (path.startsWith('http')) {
    return path
  }

  const normalizedBase = apiBaseUrl.endsWith('/') ? apiBaseUrl.slice(0, -1) : apiBaseUrl
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  if (normalizedPath.startsWith('/api/')) {
    return normalizedBase === '/api' ? normalizedPath : `${normalizedBase}${normalizedPath.slice(4)}`
  }

  return `${normalizedBase}${normalizedPath}`
}

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = (await response.json().catch(() => null)) as ApiEnvelope<T> | ApiErrorEnvelope | null

  if (!response.ok || payload?.success === false) {
    const errorPayload = payload as ApiErrorEnvelope | null
    throw new ApiError(
      errorPayload?.error?.message ?? `Request failed with HTTP ${response.status}`,
      errorPayload?.error?.code ?? 'REQUEST_FAILED',
      response.status,
    )
  }

  return (payload as ApiEnvelope<T>).data
}

export async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const url = buildUrl(path)
  const response = init === undefined ? await fetch(url) : await fetch(url, init)
  return parseResponse<T>(response)
}

export async function sendJson<T>(path: string, method: string, body?: unknown, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    ...init,
    method,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  return parseResponse<T>(response)
}

export async function sendForm<T>(path: string, method: string, formData: FormData, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    ...init,
    method,
    headers: init?.headers,
    body: formData,
  })
  return parseResponse<T>(response)
}

export function adminHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
  }
}

export function apiPath(path: string) {
  return buildUrl(path)
}
