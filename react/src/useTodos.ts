import { useCallback, useEffect, useState } from 'react'
import {
  API_BASE,
  createTodo,
  deleteTodo,
  listTodos,
  updateTodo,
  type Todo,
  type TodoEvent,
} from './api'

// loading: first request is running. error: the first request failed.
type Status = 'loading' | 'ready' | 'error'

function toMessage(e: unknown): string {
  return e instanceof Error ? e.message : String(e)
}

// Add a Todo, or replace the one with the same id. Keeps the id order.
function upsert(todos: Todo[], todo: Todo): Todo[] {
  const rest = todos.filter((t) => t.id !== todo.id)
  return [...rest, todo].sort((a, b) => a.id - b.id)
}

function without(todos: Todo[], id: number): Todo[] {
  return todos.filter((t) => t.id !== id)
}

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [status, setStatus] = useState<Status>('loading')
  const [error, setError] = useState<string | null>(null)
  const [live, setLive] = useState(false)

  const reload = useCallback(
    () =>
      listTodos().then(
        (items) => {
          setTodos(items)
          setStatus('ready')
          setError(null)
        },
        (e: unknown) => {
          setStatus('error')
          setError(toMessage(e))
        },
      ),
    [],
  )

  useEffect(() => {
    void reload()
  }, [reload])

  // Live updates over Server-Sent Events.
  // A change we made ourselves arrives here too, so every update below
  // gives the same result when it is applied twice.
  useEffect(() => {
    const source = new EventSource(`${API_BASE}/todos/events`)
    let wasOpen = false

    source.onopen = () => {
      setLive(true)
      // After a reconnect the backend may have restarted with new data.
      if (wasOpen) void reload()
      wasOpen = true
    }
    // The browser reconnects by itself. We only show the state.
    source.onerror = () => setLive(false)

    const onChange = (e: MessageEvent<string>) => {
      const event = JSON.parse(e.data) as TodoEvent
      const { todo } = event
      setTodos((prev) =>
        todo ? upsert(prev, todo) : without(prev, event.todo_id),
      )
    }
    source.addEventListener('created', onChange)
    source.addEventListener('updated', onChange)
    source.addEventListener('deleted', onChange)

    return () => source.close()
  }, [reload])

  // Run one change. Returns false and keeps the message when it fails.
  const run = useCallback(async (change: () => Promise<void>) => {
    try {
      await change()
      setError(null)
      return true
    } catch (e) {
      setError(toMessage(e))
      return false
    }
  }, [])

  const add = (title: string) =>
    run(async () => {
      const todo = await createTodo(title)
      setTodos((prev) => upsert(prev, todo))
    })

  const toggle = (todo: Todo) =>
    run(async () => {
      const next = await updateTodo(todo.id, { done: !todo.done })
      setTodos((prev) => upsert(prev, next))
    })

  const remove = (id: number) =>
    run(async () => {
      await deleteTodo(id)
      setTodos((prev) => without(prev, id))
    })

  return { todos, status, error, live, reload, add, toggle, remove }
}
