// Client for the Todo API (fastapi).
// In development, Vite forwards /api/* to the backend. See vite.config.ts.

export type Todo = {
  id: number
  title: string
  done: boolean
  created_at: string // ISO 8601
}

export type TodoUpdate = {
  title?: string
  done?: boolean
}

// One change to a Todo. The backend sends it on the event stream.
export type TodoEvent = {
  id: number
  type: 'created' | 'updated' | 'deleted'
  todo_id: number
  todo: Todo | null // null for "deleted"
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export const API_BASE = '/api'

// FastAPI puts the reason in "detail".
// It is a string, or a list of { msg } objects for a 422.
function detailToMessage(detail: unknown): string | null {
  if (typeof detail === 'string') return detail
  if (!Array.isArray(detail)) return null
  const messages = detail.flatMap((item: unknown) =>
    typeof item === 'object' &&
    item !== null &&
    'msg' in item &&
    typeof item.msg === 'string'
      ? [item.msg]
      : [],
  )
  return messages.length > 0 ? messages.join(', ') : null
}

async function errorMessage(res: Response): Promise<string> {
  try {
    const body: unknown = await res.json()
    if (typeof body === 'object' && body !== null && 'detail' in body) {
      const message = detailToMessage(body.detail)
      if (message) return message
    }
  } catch {
    // The body is not JSON. Use the status line.
  }
  return res.statusText || `HTTP ${res.status}`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(API_BASE + path, init)
  if (!res.ok) throw new ApiError(res.status, await errorMessage(res))
  // 204 No Content has no body.
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

function withJson(method: string, body: unknown): RequestInit {
  return {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }
}

export function listTodos(): Promise<Todo[]> {
  return request('/todos?limit=100')
}

export function createTodo(title: string): Promise<Todo> {
  return request('/todos', withJson('POST', { title }))
}

export function updateTodo(id: number, patch: TodoUpdate): Promise<Todo> {
  return request(`/todos/${id}`, withJson('PATCH', patch))
}

export function deleteTodo(id: number): Promise<void> {
  return request(`/todos/${id}`, { method: 'DELETE' })
}
