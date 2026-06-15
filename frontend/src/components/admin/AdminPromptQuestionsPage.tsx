import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'

import { adminService, type PromptQuestionPayload } from '../../services/admin'
import type { PromptQuestion } from '../../services/types'
import { useAdminResource } from './useAdminResource'

type AdminPageProps = {
  token: string
}

const emptyQuestion: PromptQuestionPayload = {
  question: '',
  category: 'interview',
  sort_order: 0,
  status: 'published',
}

export function AdminPromptQuestionsPage({ token }: AdminPageProps) {
  const loader = useCallback(() => adminService.listPromptQuestions(token), [token])
  const { data: questions, loading, error, reload, setError } = useAdminResource<PromptQuestion[]>(loader, [])
  const [form, setForm] = useState<PromptQuestionPayload>(emptyQuestion)
  const [saving, setSaving] = useState(false)

  async function createQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await adminService.createPromptQuestion(token, form)
      setForm(emptyQuestion)
      await reload()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  async function updateQuestion(questionId: number, payload: Partial<PromptQuestionPayload>) {
    await adminService.updatePromptQuestion(token, questionId, payload)
    await reload()
  }

  async function deleteQuestion(questionId: number) {
    await adminService.deletePromptQuestion(token, questionId)
    await reload()
  }

  return (
    <div className="admin-panel">
      <form className="admin-form admin-form-grid" onSubmit={(event) => void createQuestion(event)}>
        <label className="wide">
          问题
          <input value={form.question} onChange={(event) => setForm({ ...form, question: event.target.value })} required />
        </label>
        <label>
          分类
          <input value={form.category ?? ''} onChange={(event) => setForm({ ...form, category: event.target.value })} />
        </label>
        <label>
          排序
          <input
            type="number"
            value={form.sort_order}
            onChange={(event) => setForm({ ...form, sort_order: Number(event.target.value) })}
          />
        </label>
        <label>
          状态
          <select
            value={form.status}
            onChange={(event) => setForm({ ...form, status: event.target.value as PromptQuestionPayload['status'] })}
          >
            <option value="published">published</option>
            <option value="draft">draft</option>
            <option value="hidden">hidden</option>
          </select>
        </label>
        <button className="btn btn-primary" disabled={saving} type="submit">
          {saving ? '保存中...' : '新增问题'}
        </button>
      </form>

      {error ? <p className="inline-error">{error}</p> : null}
      {loading ? <p className="loading-line">正在加载预设问题...</p> : null}

      <div className="admin-list">
        {questions.map((question) => (
          <article className="admin-row" key={question.id}>
            <div>
              <strong>{question.question}</strong>
              <p>
                {question.category || '未分类'} · sort {question.sort_order}
              </p>
            </div>
            <div className="admin-row-actions">
              <select
                value={question.status ?? 'published'}
                onChange={(event) =>
                  void updateQuestion(question.id, { status: event.target.value as PromptQuestionPayload['status'] })
                }
              >
                <option value="published">published</option>
                <option value="draft">draft</option>
                <option value="hidden">hidden</option>
              </select>
              <input
                aria-label={`${question.question} 排序`}
                type="number"
                value={question.sort_order}
                onChange={(event) => void updateQuestion(question.id, { sort_order: Number(event.target.value) })}
              />
              <button className="danger-button" type="button" onClick={() => void deleteQuestion(question.id)}>
                删除
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
