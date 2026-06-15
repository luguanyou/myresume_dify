import { getJson } from './client'
import type { ProjectDetail, ProjectListItem } from './types'

export const projectService = {
  getFeaturedProjects() {
    return getJson<ProjectListItem[]>('/projects?featured=true')
  },

  getProjects() {
    return getJson<ProjectListItem[]>('/projects')
  },

  getProjectDetail(projectId: number) {
    return getJson<ProjectDetail>(`/projects/${projectId}`)
  },
}
