import { describe, expect, test, vi } from 'vitest'

import { adminService } from './admin'
import { streamChat } from './chat'
import { projectService } from './projects'
import { resumeDownloadUrl } from './public'
import { getProjectRoute, portfolioHomePath, projectDetailPath } from '../routes'

function jsonResponse(data: unknown, init?: ResponseInit) {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
}

describe('projectService', () => {
  test('requests featured projects from the public API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        success: true,
        data: [{ id: 1, title: 'AI Resume Assistant', tech_stack: ['React'] }],
        message: 'ok',
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const projects = await projectService.getFeaturedProjects()

    expect(fetchMock).toHaveBeenCalledWith('/dify/api/projects?featured=true')
    expect(projects).toHaveLength(1)
    expect(projects[0].title).toBe('AI Resume Assistant')
  })

  test('requests project detail by id from the public API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        success: true,
        data: {
          id: 42,
          slug: 'ai-resume-assistant',
          title: 'AI Resume Assistant',
          subtitle: 'Askable resume',
          summary: 'A public project detail.',
          project_type: 'AI App',
          role: 'Frontend and API integration',
          tech_stack: ['React', 'FastAPI'],
          cover_media: null,
          is_featured: true,
          sort_order: 100,
          background: 'Interviewers need concrete evidence.',
          goals: 'Show project depth.',
          features: ['Project detail page'],
          challenges: ['Streaming answer UX'],
          solutions: ['SSE rendering'],
          links: [],
          media: [],
        },
        message: 'ok',
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const project = await projectService.getProjectDetail(42)

    expect(fetchMock).toHaveBeenCalledWith('/dify/api/projects/42')
    expect(project.title).toBe('AI Resume Assistant')
    expect(project.features).toEqual(['Project detail page'])
  })
})

describe('public routes', () => {
  test('recognizes public project detail paths', () => {
    expect(getProjectRoute('/projects/42')).toEqual({ projectId: 42 })
    expect(getProjectRoute('/dify/projects/42')).toEqual({ projectId: 42 })
  })

  test('ignores invalid project detail paths', () => {
    expect(getProjectRoute('/projects/not-a-number')).toBeNull()
    expect(getProjectRoute('/projects/42/edit')).toBeNull()
    expect(getProjectRoute('/admin/projects/42')).toBeNull()
  })

  test('generates public paths for root and dify base deployments', () => {
    expect(projectDetailPath(42, '/')).toBe('/projects/42')
    expect(projectDetailPath(42, '/dify/')).toBe('/dify/projects/42')
    expect(portfolioHomePath('/projects/42')).toBe('/')
    expect(portfolioHomePath('/dify/projects/42')).toBe('/dify/')
  })
})

describe('adminService', () => {
  test('sends bearer token for admin requests', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        success: true,
        data: [],
        message: 'ok',
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await adminService.listProjects('token-123')

    expect(fetchMock).toHaveBeenCalledWith('/dify/api/admin/projects', {
      headers: {
        Authorization: 'Bearer token-123',
      },
    })
  })
})

describe('streamChat', () => {
  test('parses SSE message chunks and done events', async () => {
    const encoder = new TextEncoder()
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(
          encoder.encode(
            'event: message\ndata: {"answer":"Hello","conversation_id":"c1"}\n\n' +
              'event: message\ndata: {"answer":" world","conversation_id":"c1"}\n\n' +
              'event: done\ndata: {"conversation_id":"c1"}\n\n',
          ),
        )
        controller.close()
      },
    })
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(stream, {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const chunks: string[] = []
    let doneConversationId = ''
    await streamChat(
      { message: 'Introduce yourself', visitor_id: 'test-user' },
      {
        onMessage(chunk) {
          chunks.push(chunk.answer)
        },
        onDone(conversationId) {
          doneConversationId = conversationId
        },
      },
    )

    expect(fetchMock).toHaveBeenCalledWith(
      '/dify/api/chat/stream',
      expect.objectContaining({
        body: JSON.stringify({ message: 'Introduce yourself', visitor_id: 'test-user' }),
        method: 'POST',
      }),
    )
    expect(chunks.join('')).toBe('Hello world')
    expect(doneConversationId).toBe('c1')
  })

  test('filters private reasoning tags from streamed answer chunks', async () => {
    const encoder = new TextEncoder()
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(
          encoder.encode(
            'event: message\ndata: {"answer":"<thi","conversation_id":"c2"}\n\n' +
              'event: message\ndata: {"answer":"nk>hidden reasoning","conversation_id":"c2"}\n\n' +
              'event: message\ndata: {"answer":"</think>Visible answer","conversation_id":"c2"}\n\n' +
              'event: done\ndata: {"conversation_id":"c2"}\n\n',
          ),
        )
        controller.close()
      },
    })
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(stream, {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const chunks: string[] = []
    await streamChat(
      { message: 'Say hello', visitor_id: 'test-user' },
      {
        onMessage(chunk) {
          chunks.push(chunk.answer)
        },
      },
    )

    expect(chunks.join('')).toBe('Visible answer')
    expect(chunks.join('')).not.toContain('think')
    expect(chunks.join('')).not.toContain('hidden reasoning')
  })
})

describe('publicService urls', () => {
  test('uses the /dify API prefix for resume downloads', () => {
    expect(resumeDownloadUrl).toBe('/dify/api/resume/download')
  })
})
