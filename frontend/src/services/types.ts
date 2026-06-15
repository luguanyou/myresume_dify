export type ApiEnvelope<T> = {
  success: boolean
  data: T
  message: string
}

export type ApiErrorEnvelope = {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

export type MediaAsset = {
  id: number
  project_id?: number | null
  media_type: 'image' | 'video' | 'document' | string
  purpose?: string | null
  original_filename?: string | null
  stored_filename?: string | null
  url?: string | null
  public_url?: string | null
  mime_type?: string | null
  file_ext?: string | null
  file_size?: number | null
  width?: number | null
  height?: number | null
  duration_seconds?: number | null
  alt_text?: string | null
  sort_order?: number
  status?: 'draft' | 'published' | 'hidden' | string
  metadata?: Record<string, unknown>
  created_at?: string | null
}

export type CoverMedia = {
  id: number
  url: string
  media_type: string
}

export type ProjectListItem = {
  id: number
  slug: string
  title: string
  subtitle?: string | null
  summary: string
  project_type: string
  role?: string | null
  tech_stack: string[]
  cover_media?: CoverMedia | null
  is_featured: boolean
  sort_order: number
}

export type ProjectDetail = ProjectListItem & {
  background?: string | null
  goals?: string | null
  features: string[]
  challenges: string[]
  solutions: string[]
  links: Array<{ label?: string; url?: string; link_type?: string }>
  media: MediaAsset[]
}

export type Resume = {
  id: number
  title: string
  media_id: number
  version_label?: string | null
  download_url: string
  updated_at?: string | null
}

export type SiteProfile = {
  id?: number
  owner_name: string
  headline: string
  summary?: string | null
  email?: string | null
  phone?: string | null
  wechat?: string | null
  github_url?: string | null
  portfolio_url?: string | null
  extra_links?: Array<{ label?: string; url?: string }>
  status?: 'published' | 'hidden'
  created_at?: string | null
  updated_at?: string | null
}

export type PromptQuestion = {
  id: number
  question: string
  category?: string | null
  sort_order: number
  status?: 'draft' | 'published' | 'hidden'
  created_at?: string | null
  updated_at?: string | null
}

export type AdminUser = {
  id: number
  username: string
  display_name?: string | null
  email?: string | null
  status: string
  last_login_at?: string | null
}

export type LoginResponse = {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  admin: AdminUser
}

export type AdminProject = {
  id: number
  slug: string
  title: string
  subtitle?: string | null
  summary: string
  project_type: string
  background?: string | null
  goals?: string | null
  role?: string | null
  features: string[]
  challenges: string[]
  solutions: string[]
  tech_stack: string[]
  links: Array<{ label?: string; url?: string; link_type?: string }>
  cover_media_id?: number | null
  status: 'draft' | 'published' | 'hidden'
  is_featured: boolean
  sort_order: number
  created_at?: string | null
  updated_at?: string | null
}

export type AdminResume = Resume & {
  is_current: boolean
  status: string
  media?: MediaAsset | null
  created_at?: string | null
}
