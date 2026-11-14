import type { Todo } from '../api'

type TodoListProps = {
  todos: Todo[]
  onToggle: (todo: Todo) => void
  onRemove: (id: number) => void
}

export function TodoList({ todos, onToggle, onRemove }: TodoListProps) {
  if (todos.length === 0) {
    return <p className="empty">No todos yet.</p>
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <li key={todo.id}>
          <label>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => onToggle(todo)}
            />
            <span className={todo.done ? 'done' : undefined}>{todo.title}</span>
          </label>
          <button
            type="button"
            className="remove"
            aria-label={`Delete ${todo.title}`}
            onClick={() => onRemove(todo.id)}
          >
            ×
          </button>
        </li>
      ))}
    </ul>
  )
}
