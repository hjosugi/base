import { describe, expect, it, vi } from 'vitest'
import { ApiError, createTodo, deleteTodo, listTodos } from './api'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

// Replace fetch for one test. Returns the mock so the test can check calls.
function stubFetch(response: Response) {
  const fetchMock = vi.fn(async () => response)
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('api', () => {
  it('lists todos under /api', async () => {
    const todo = { id: 1, title: 'a', done: false, created_at: '2026-01-01' }
    const fetchMock = stubFetch(jsonResponse([todo]))

    await expect(listTodos()).resolves.toEqual([todo])
    expect(fetchMock).toHaveBeenCalledWith('/api/todos?limit=100', undefined)
  })

  it('sends the title as JSON', async () => {
    const fetchMock = stubFetch(jsonResponse({ id: 1 }, 201))

    await createTodo('Buy milk')

    expect(fetchMock).toHaveBeenCalledWith('/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{"title":"Buy milk"}',
    })
  })

  it('returns nothing for 204', async () => {
    stubFetch(new Response(null, { status: 204 }))

    await expect(deleteTodo(1)).resolves.toBeUndefined()
  })

  it('uses the FastAPI "detail" text as the error message', async () => {
    stubFetch(jsonResponse({ detail: 'Todo 9 not found' }, 404))

    const error = await deleteTodo(9).catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 404, message: 'Todo 9 not found' })
  })

  it('joins the messages of a 422 validation error', async () => {
    const detail = [
      {
        loc: ['body', 'title'],
        msg: 'String should have at least 1 character',
      },
    ]
    stubFetch(jsonResponse({ detail }, 422))

    await expect(createTodo('')).rejects.toThrow(
      'String should have at least 1 character',
    )
  })
})
