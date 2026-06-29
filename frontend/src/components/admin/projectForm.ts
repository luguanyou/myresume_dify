import type { ProjectPayload } from '../../services/admin'
import type { AdminProject } from '../../services/types'

export type ProjectFormState = {
  slug: string
  title: string
  subtitle: string
  summary: string
  project_type: string
  background: string
  goals: string
  role: string
  status: ProjectPayload['status']
  is_featured: boolean
  sort_order: number
  cover_media_id_text: string
  tech_stack_text: string
  features_text: string
  challenges_text: string
  solutions_text: string
  links_text: string
}

export const emptyProjectFormState: ProjectFormState = {
  slug: '',
  title: '',
  subtitle: '',
  summary: '',
  project_type: 'AI 应用',
  background: '',
  goals: '',
  role: '',
  status: 'published',
  is_featured: true,
  sort_order: 0,
  cover_media_id_text: '',
  tech_stack_text: '',
  features_text: '',
  challenges_text: '',
  solutions_text: '',
  links_text: '',
}

export function linesToArray(value: string) {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

export function linksTextToArray(value: string) {
  return linesToArray(value).map((line) => {
    const [rawLabel, rawUrl, rawType] = line.split('|').map((item) => item.trim())
    const url = rawUrl || rawLabel

    return {
      label: rawLabel,
      url,
      link_type: rawType || '',
    }
  })
}

export function linksToText(links: Array<{ label?: string; url?: string; link_type?: string }> = []) {
  return links
    .filter((link) => link.url?.trim())
    .map((link) => [link.label || link.url || '', link.url || '', link.link_type || ''].join(' | '))
    .join('\n')
}

function nullableText(value: string) {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

function optionalMediaId(value: string) {
  const trimmed = value.trim()
  return trimmed ? Number(trimmed) : null
}

export function projectToFormState(project: AdminProject): ProjectFormState {
  return {
    slug: project.slug,
    title: project.title,
    subtitle: project.subtitle ?? '',
    summary: project.summary,
    project_type: project.project_type,
    background: project.background ?? '',
    goals: project.goals ?? '',
    role: project.role ?? '',
    status: project.status,
    is_featured: project.is_featured,
    sort_order: project.sort_order,
    cover_media_id_text: project.cover_media_id == null ? '' : String(project.cover_media_id),
    tech_stack_text: project.tech_stack.join('\n'),
    features_text: project.features.join('\n'),
    challenges_text: project.challenges.join('\n'),
    solutions_text: project.solutions.join('\n'),
    links_text: linksToText(project.links),
  }
}

export function formStateToPayload(form: ProjectFormState): ProjectPayload {
  return {
    slug: form.slug,
    title: form.title,
    subtitle: nullableText(form.subtitle),
    summary: form.summary,
    project_type: form.project_type,
    background: nullableText(form.background),
    goals: nullableText(form.goals),
    role: nullableText(form.role),
    tech_stack: linesToArray(form.tech_stack_text),
    features: linesToArray(form.features_text),
    challenges: linesToArray(form.challenges_text),
    solutions: linesToArray(form.solutions_text),
    links: linksTextToArray(form.links_text),
    cover_media_id: optionalMediaId(form.cover_media_id_text),
    status: form.status,
    is_featured: form.is_featured,
    sort_order: form.sort_order,
  }
}
