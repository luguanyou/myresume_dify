import { apiPath } from './client'

export type ChatStreamPayload = {
  message: string
  conversation_id?: string
  visitor_id?: string
}

export type ChatMessageChunk = {
  answer: string
  conversation_id?: string
}

export type ChatStreamHandlers = {
  onMessage: (chunk: ChatMessageChunk) => void
  onDone?: (conversationId: string) => void
  onError?: (message: string, code?: string) => void
}

type SseEvent = {
  event: string
  data: string
}

function parseSseBlock(block: string): SseEvent | null {
  const eventLine = block
    .split('\n')
    .map((line) => line.trimEnd())
    .find((line) => line.startsWith('event:'))
  const dataLines = block
    .split('\n')
    .map((line) => line.trimEnd())
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())

  if (!eventLine || dataLines.length === 0) {
    return null
  }

  return {
    event: eventLine.slice(6).trim(),
    data: dataLines.join('\n'),
  }
}

function handleEvent(event: SseEvent, handlers: ChatStreamHandlers) {
  const payload = JSON.parse(event.data) as Record<string, string | undefined>

  if (event.event === 'message') {
    handlers.onMessage({
      answer: payload.answer ?? '',
      conversation_id: payload.conversation_id,
    })
    return
  }

  if (event.event === 'done') {
    handlers.onDone?.(payload.conversation_id ?? '')
    return
  }

  if (event.event === 'error') {
    handlers.onError?.(payload.message ?? 'AI service is temporarily unavailable', payload.code)
  }
}

export async function streamChat(payload: ChatStreamPayload, handlers: ChatStreamHandlers) {
  const response = await fetch(apiPath('/chat/stream'), {
    method: 'POST',
    headers: {
      Accept: 'text/event-stream',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok || !response.body) {
    handlers.onError?.(`Chat request failed with HTTP ${response.status}`, 'REQUEST_FAILED')
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split(/\n\n/)
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      const event = parseSseBlock(block)
      if (event) {
        handleEvent(event, handlers)
      }
    }
  }

  buffer += decoder.decode()
  const trailingEvent = parseSseBlock(buffer)
  if (trailingEvent) {
    handleEvent(trailingEvent, handlers)
  }
}
