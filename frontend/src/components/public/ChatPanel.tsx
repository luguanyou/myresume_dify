import { useMemo, useRef, useState } from 'react'
import type { FormEvent } from 'react'

import { streamChat } from '../../services/chat'
import type { PromptQuestion } from '../../services/types'

type ChatPanelProps = {
  prompts: PromptQuestion[]
}

type Message = {
  id: string
  role: 'assistant' | 'user'
  content: string
  sources?: string[]
}

const initialMessages: Message[] = [
  {
    id: 'intro',
    role: 'assistant',
    content:
      '你好，我是卢官有的 AI 简历助手。你可以直接问他的项目经历、技术栈、个人职责和岗位匹配度。',
    sources: ['AI 简历助手', '项目材料', '技术栈说明'],
  },
]

function visitorId() {
  const storageKey = 'portfolioVisitorId'
  const existing = window.localStorage.getItem(storageKey)
  if (existing) {
    return existing
  }

  const generated = `web-${crypto.randomUUID()}`
  window.localStorage.setItem(storageKey, generated)
  return generated
}

export function ChatPanel({ prompts }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState('')
  const activeAssistantId = useRef('')

  const visiblePrompts = useMemo(() => prompts.slice(0, 5), [prompts])

  async function sendMessage(rawMessage: string) {
    const message = rawMessage.trim()
    if (!message || isStreaming) {
      return
    }

    const userMessageId = `user-${crypto.randomUUID()}`
    const assistantMessageId = `assistant-${crypto.randomUUID()}`
    activeAssistantId.current = assistantMessageId
    setMessages((current) => [
      ...current,
      { id: userMessageId, role: 'user', content: message },
      { id: assistantMessageId, role: 'assistant', content: '' },
    ])
    setInput('')
    setError('')
    setIsStreaming(true)

    await streamChat(
      {
        message,
        conversation_id: conversationId,
        visitor_id: visitorId(),
      },
      {
        onMessage(chunk) {
          if (chunk.conversation_id) {
            setConversationId(chunk.conversation_id)
          }
          setMessages((current) =>
            current.map((item) =>
              item.id === activeAssistantId.current ? { ...item, content: item.content + chunk.answer } : item,
            ),
          )
        },
        onDone(nextConversationId) {
          if (nextConversationId) {
            setConversationId(nextConversationId)
          }
          setIsStreaming(false)
        },
        onError(messageText) {
          setError(messageText)
          setIsStreaming(false)
          setMessages((current) =>
            current.map((item) =>
              item.id === activeAssistantId.current && !item.content
                ? { ...item, content: 'AI 服务暂时不可用，请稍后重试。' }
                : item,
            ),
          )
        },
      },
    )

    setIsStreaming(false)
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void sendMessage(input)
  }

  function clearConversation() {
    setConversationId('')
    setMessages(initialMessages)
    setError('')
  }

  return (
    <section className="chat-panel" id="assistant" aria-label="AI 简历对话">
      <div className="chat-top">
        <div className="chat-title">
          <span className="assistant-icon">AI</span>
          <div>
            <strong>直接问我的简历和项目</strong>
            <span>支持追问项目细节、技术栈、岗位匹配度，回答会尽量基于可验证材料。</span>
          </div>
        </div>
        <span className="live-badge">
          <span className="status-dot"></span>
          {isStreaming ? '回答中' : '可对话'}
        </span>
      </div>

      <div className="chat-body">
        <div className="chat-toolbar">
          <p className="quick-label">面试官常问</p>
          <button className="ghost-button" type="button" onClick={clearConversation}>
            清空
          </button>
        </div>
        <div className="prompt-grid">
          {visiblePrompts.map((prompt, index) => (
            <button
              className={`prompt ${index === 0 ? 'primary' : ''}`}
              disabled={isStreaming}
              key={prompt.id}
              type="button"
              onClick={() => void sendMessage(prompt.question)}
            >
              {prompt.question}
            </button>
          ))}
        </div>

        <div className="conversation" aria-live="polite" aria-label="对话列表">
          {messages.map((message) => (
            <div className={`message ${message.role === 'user' ? 'user' : ''}`} key={message.id}>
              {message.role === 'assistant' ? <span className="avatar">AI</span> : null}
              <div className="bubble">
                {message.content ? (
                  message.content.split('\n').map((paragraph) => <p key={`${message.id}-${paragraph}`}>{paragraph}</p>)
                ) : (
                  <span className="typing" aria-hidden="true">
                    <i></i>
                    <i></i>
                    <i></i>
                  </span>
                )}
                {message.sources ? (
                  <div className="source-row" aria-label="回答来源">
                    {message.sources.map((source) => (
                      <span className="source" key={source}>
                        来源：{source}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
        {error ? <p className="inline-error">{error}</p> : null}
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          aria-label="聊天输入框"
          disabled={isStreaming}
          placeholder="例如：讲讲你的 Dify 项目、后端接口、岗位匹配度..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
        />
        <button className="send-button" disabled={isStreaming || !input.trim()} type="submit" aria-label="发送">
          ↑
        </button>
      </form>
    </section>
  )
}
