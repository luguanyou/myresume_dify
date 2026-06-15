import { describe, expect, test, vi } from 'vitest'

import { adminService } from './admin'
import { streamChat } from './chat'
import { projectService } from './projects'

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

    expect(fetchMock).toHaveBeenCalledWith('/api/projects?featured=true')
    expect(projects).toHaveLength(1)
    expect(projects[0].title).toBe('AI Resume Assistant')
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

    expect(fetchMock).toHaveBeenCalledWith('/api/admin/projects', {
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
      '/api/chat/stream',
      expect.objectContaining({
        body: JSON.stringify({ message: 'Introduce yourself', visitor_id: 'test-user' }),
        method: 'POST',
      }),
    )
    expect(chunks.join('')).toBe('Hello world')
    expect(doneConversationId).toBe('c1')
  })
})
