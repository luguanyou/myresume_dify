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

type PrivateReasoningFilter = {
  insideReasoning: boolean
  pending: string
}

const reasoningStartTag = /<think(?:ing)?(?:\s[^>]*)?>/i
const reasoningEndTag = /<\/think(?:ing)?\s*>/i
const reasoningStartPrefixes = ['<think', '<thinking']
const reasoningEndPrefixes = ['</think', '</thinking']

function createPrivateReasoningFilter(): PrivateReasoningFilter {
  return {
    insideReasoning: false,
    pending: '',
  }
}

function isPotentialTagFragment(fragment: string, prefixes: string[]) {
  const lowerFragment = fragment.toLowerCase()
  return !lowerFragment.includes('>') && prefixes.some((prefix) => prefix.startsWith(lowerFragment) || lowerFragment.startsWith(prefix))
}

function findPotentialTagFragmentStart(text: string, prefixes: string[]) {
  for (let index = 0; index < text.length; index += 1) {
    if (text[index] === '<' && isPotentialTagFragment(text.slice(index), prefixes)) {
      return index
    }
  }

  return -1
}

function filterPrivateReasoningChunk(filter: PrivateReasoningFilter, chunk: string) {
  filter.pending += chunk
  let visibleText = ''

  while (filter.pending) {
    if (filter.insideReasoning) {
      const endMatch = reasoningEndTag.exec(filter.pending)
      if (!endMatch) {
        const partialEndIndex = findPotentialTagFragmentStart(filter.pending, reasoningEndPrefixes)
        filter.pending = partialEndIndex === -1 ? '' : filter.pending.slice(partialEndIndex)
        break
      }

      filter.pending = filter.pending.slice(endMatch.index + endMatch[0].length)
      filter.insideReasoning = false
      continue
    }

    const startMatch = reasoningStartTag.exec(filter.pending)
    if (!startMatch) {
      const partialStartIndex = findPotentialTagFragmentStart(filter.pending, reasoningStartPrefixes)
      if (partialStartIndex === -1) {
        visibleText += filter.pending
        filter.pending = ''
      } else {
        visibleText += filter.pending.slice(0, partialStartIndex)
        filter.pending = filter.pending.slice(partialStartIndex)
      }
      break
    }

    visibleText += filter.pending.slice(0, startMatch.index)
    filter.pending = filter.pending.slice(startMatch.index + startMatch[0].length)
    filter.insideReasoning = true
  }

  return visibleText
}

function flushPrivateReasoningFilter(filter: PrivateReasoningFilter) {
  if (filter.insideReasoning || isPotentialTagFragment(filter.pending, reasoningStartPrefixes)) {
    filter.insideReasoning = false
    filter.pending = ''
    return ''
  }

  const visibleText = filter.pending
  filter.pending = ''
  return visibleText
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

function handleEvent(event: SseEvent, handlers: ChatStreamHandlers, reasoningFilter: PrivateReasoningFilter) {
  const payload = JSON.parse(event.data) as Record<string, string | undefined>

  if (event.event === 'message') {
    handlers.onMessage({
      answer: filterPrivateReasoningChunk(reasoningFilter, payload.answer ?? ''),
      conversation_id: payload.conversation_id,
    })
    return
  }

  if (event.event === 'done') {
    const remainingAnswer = flushPrivateReasoningFilter(reasoningFilter)
    if (remainingAnswer) {
      handlers.onMessage({
        answer: remainingAnswer,
        conversation_id: payload.conversation_id,
      })
    }
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
  const reasoningFilter = createPrivateReasoningFilter()
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
        handleEvent(event, handlers, reasoningFilter)
      }
    }
  }

  buffer += decoder.decode()
  const trailingEvent = parseSseBlock(buffer)
  if (trailingEvent) {
    handleEvent(trailingEvent, handlers, reasoningFilter)
  }
}
