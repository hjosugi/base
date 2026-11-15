import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import type { Todo, TodoEvent } from './api'

const milk: Todo = {
  id: 1,
  title: 'Buy milk',
  done: false,
  created_at: '2026-01-01T00:00:00Z',
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

// jsdom has no EventSource. This one lets a test send an event by hand.
class FakeEventSource {
  static last: FakeEventSource | undefined

  onopen: (() => void) | null = null
  onerror: (() => void) | null = null
  private listeners = new Map<string, (e: MessageEvent<string>) => void>()

  constructor() {
    FakeEventSource.last = this
  }

  addEventListener(type: string, listener: (e: MessageEvent<string>) => void) {
    this.listeners.set(type, listener)
  }

  close() {}

  emit(event: TodoEvent) {
    const message = new MessageEvent(event.type, {
      data: JSON.stringify(event),
    })
    this.listeners.get(event.type)?.(message)
  }
}

describe('App', () => {
  beforeEach(() => {
    vi.stubGlobal('EventSource', FakeEventSource)
  })

  it('shows the todos from the API', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => jsonResponse([milk])),
    )

    render(<App />)

    expect(await screen.findByText('Buy milk')).toBeInTheDocument()
    expect(screen.getByText('0 / 1 done')).toBeInTheDocument()
  })

  it('adds a todo from the form', async () => {
    const created: Todo = { ...milk, id: 2, title: 'Write tests' }
    const fetchMock = vi.fn(async (_url: string, init?: RequestInit) =>
      init?.method === 'POST' ? jsonResponse(created, 201) : jsonResponse([]),
    )
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<App />)
    await user.type(await screen.findByLabelText('New todo'), 'Write tests')
    await user.click(screen.getByRole('button', { name: 'Add' }))

    expect(await screen.findByText('Write tests')).toBeInTheDocument()
    expect(screen.getByLabelText('New todo')).toHaveValue('')
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/todos',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('applies a change from the event stream', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => jsonResponse([])),
    )

    render(<App />)
    await screen.findByText('No todos yet.')
    act(() => {
      FakeEventSource.last?.emit({
        id: 1,
        type: 'created',
        todo_id: 1,
        todo: milk,
      })
    })

    expect(screen.getByText('Buy milk')).toBeInTheDocument()
  })

  it('tells how to start the backend when the API is down', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response('', { status: 500 })),
    )

    render(<App />)

    expect(await screen.findByText(/uv run fastapi dev/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })
})
