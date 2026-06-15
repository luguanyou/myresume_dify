import { apiPath, getJson } from './client'
import type { PromptQuestion, Resume, SiteProfile } from './types'

export const resumeDownloadUrl = apiPath('/resume/download')

export const publicService = {
  getSiteProfile() {
    return getJson<SiteProfile>('/site/profile')
  },

  getPromptQuestions() {
    return getJson<PromptQuestion[]>('/prompt-questions')
  },

  getCurrentResume() {
    return getJson<Resume>('/resume/current')
  },
}
