import { adminHeaders, getJson, sendForm, sendJson } from './client'
import type {
  AdminProject,
  AdminResume,
  AdminUser,
  LoginResponse,
  MediaAsset,
  PromptQuestion,
  SiteProfile,
} from './types'

export type ProjectPayload = Omit<AdminProject, 'id' | 'created_at' | 'updated_at'>
export type PromptQuestionPayload = Pick<PromptQuestion, 'question' | 'category' | 'sort_order' | 'status'>
export type SiteProfilePayload = Required<Pick<SiteProfile, 'owner_name' | 'headline'>> &
  Omit<SiteProfile, 'id' | 'created_at' | 'updated_at'>

export const adminService = {
  login(username: string, password: string) {
    return sendJson<LoginResponse>('/admin/auth/login', 'POST', { username, password })
  },

  me(token: string) {
    return getJson<AdminUser>('/admin/auth/me', { headers: adminHeaders(token) })
  },

  logout(token: string) {
    return sendJson<{ logged_out: boolean }>('/admin/auth/logout', 'POST', undefined, {
      headers: adminHeaders(token),
    })
  },

  listProjects(token: string) {
    return getJson<AdminProject[]>('/admin/projects', { headers: adminHeaders(token) })
  },

  createProject(token: string, payload: ProjectPayload) {
    return sendJson<AdminProject>('/admin/projects', 'POST', payload, { headers: adminHeaders(token) })
  },

  updateProject(token: string, projectId: number, payload: Partial<ProjectPayload>) {
    return sendJson<AdminProject>(`/admin/projects/${projectId}`, 'PUT', payload, {
      headers: adminHeaders(token),
    })
  },

  deleteProject(token: string, projectId: number) {
    return sendJson<{ id: number; deleted: boolean }>(`/admin/projects/${projectId}`, 'DELETE', undefined, {
      headers: adminHeaders(token),
    })
  },

  listMedia(token: string) {
    return getJson<MediaAsset[]>('/admin/media', { headers: adminHeaders(token) })
  },

  uploadMedia(token: string, formData: FormData) {
    return sendForm<MediaAsset>('/admin/media', 'POST', formData, { headers: adminHeaders(token) })
  },

  updateMedia(token: string, mediaId: number, payload: Partial<MediaAsset>) {
    return sendJson<MediaAsset>(`/admin/media/${mediaId}`, 'PUT', payload, { headers: adminHeaders(token) })
  },

  deleteMedia(token: string, mediaId: number) {
    return sendJson<{ id: number; deleted: boolean }>(`/admin/media/${mediaId}`, 'DELETE', undefined, {
      headers: adminHeaders(token),
    })
  },

  listResumes(token: string) {
    return getJson<AdminResume[]>('/admin/resumes', { headers: adminHeaders(token) })
  },

  uploadResume(token: string, formData: FormData) {
    return sendForm<AdminResume>('/admin/resumes', 'POST', formData, { headers: adminHeaders(token) })
  },

  setCurrentResume(token: string, resumeId: number) {
    return sendJson<AdminResume>(`/admin/resumes/${resumeId}/current`, 'PUT', undefined, {
      headers: adminHeaders(token),
    })
  },

  getSiteProfile(token: string) {
    return getJson<SiteProfile>('/admin/site/profile', { headers: adminHeaders(token) })
  },

  updateSiteProfile(token: string, payload: SiteProfilePayload) {
    return sendJson<SiteProfile>('/admin/site/profile', 'PUT', payload, { headers: adminHeaders(token) })
  },

  listPromptQuestions(token: string) {
    return getJson<PromptQuestion[]>('/admin/prompt-questions', { headers: adminHeaders(token) })
  },

  createPromptQuestion(token: string, payload: PromptQuestionPayload) {
    return sendJson<PromptQuestion>('/admin/prompt-questions', 'POST', payload, {
      headers: adminHeaders(token),
    })
  },

  updatePromptQuestion(token: string, questionId: number, payload: Partial<PromptQuestionPayload>) {
    return sendJson<PromptQuestion>(`/admin/prompt-questions/${questionId}`, 'PUT', payload, {
      headers: adminHeaders(token),
    })
  },

  deletePromptQuestion(token: string, questionId: number) {
    return sendJson<{ id: number; deleted: boolean }>(
      `/admin/prompt-questions/${questionId}`,
      'DELETE',
      undefined,
      { headers: adminHeaders(token) },
    )
  },
}
