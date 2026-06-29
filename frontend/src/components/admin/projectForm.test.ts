import { describe, expect, test } from 'vitest'

import { projectToFormState, formStateToPayload, linksTextToArray, linksToText } from './projectForm'

describe('linksTextToArray', () => {
  test('parses project link lines into API payload links', () => {
    expect(
      linksTextToArray(
        [
          'GitHub | https://github.com/example/project | github',
          '在线演示 | https://demo.example.com | demo',
          'https://portfolio.example.com/project',
        ].join('\n'),
      ),
    ).toEqual([
      { label: 'GitHub', url: 'https://github.com/example/project', link_type: 'github' },
      { label: '在线演示', url: 'https://demo.example.com', link_type: 'demo' },
      { label: 'https://portfolio.example.com/project', url: 'https://portfolio.example.com/project', link_type: '' },
    ])
  })
})

describe('linksToText', () => {
  test('formats API project links for textarea editing', () => {
    expect(
      linksToText([
        { label: 'GitHub', url: 'https://github.com/example/project', link_type: 'github' },
        { label: '在线演示', url: 'https://demo.example.com', link_type: 'demo' },
      ]),
    ).toBe('GitHub | https://github.com/example/project | github\n在线演示 | https://demo.example.com | demo')
  })
})

describe('project form state', () => {
  test('maps an admin project into editable textarea fields', () => {
    const state = projectToFormState({
      id: 7,
      slug: 'ai-demo',
      title: 'AI Demo',
      subtitle: 'Project subtitle',
      summary: 'Short summary',
      project_type: 'AI App',
      background: 'Background text',
      goals: 'Goal text',
      role: 'Builder',
      features: ['Chat', 'Upload'],
      challenges: ['Latency'],
      solutions: ['Streaming'],
      tech_stack: ['React', 'FastAPI'],
      links: [{ label: 'Demo', url: 'https://demo.example.com', link_type: 'demo' }],
      cover_media_id: 9,
      status: 'published',
      is_featured: true,
      sort_order: 80,
    })

    expect(state.tech_stack_text).toBe('React\nFastAPI')
    expect(state.features_text).toBe('Chat\nUpload')
    expect(state.challenges_text).toBe('Latency')
    expect(state.solutions_text).toBe('Streaming')
    expect(state.links_text).toBe('Demo | https://demo.example.com | demo')
    expect(state.cover_media_id_text).toBe('9')
  })

  test('maps editable form state into a project API payload', () => {
    const payload = formStateToPayload({
      slug: 'ai-demo',
      title: 'AI Demo',
      subtitle: '',
      summary: 'Short summary',
      project_type: 'AI App',
      background: '',
      goals: '',
      role: 'Builder',
      status: 'published',
      is_featured: true,
      sort_order: 80,
      cover_media_id_text: '',
      tech_stack_text: 'React\nFastAPI',
      features_text: 'Chat\nUpload',
      challenges_text: 'Latency',
      solutions_text: 'Streaming',
      links_text: 'Demo | https://demo.example.com | demo',
    })

    expect(payload).toEqual({
      slug: 'ai-demo',
      title: 'AI Demo',
      subtitle: null,
      summary: 'Short summary',
      project_type: 'AI App',
      background: null,
      goals: null,
      role: 'Builder',
      tech_stack: ['React', 'FastAPI'],
      features: ['Chat', 'Upload'],
      challenges: ['Latency'],
      solutions: ['Streaming'],
      links: [{ label: 'Demo', url: 'https://demo.example.com', link_type: 'demo' }],
      cover_media_id: null,
      status: 'published',
      is_featured: true,
      sort_order: 80,
    })
  })
})
