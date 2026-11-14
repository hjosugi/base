import { useState } from 'react'

type TodoFormProps = {
  // Resolves to true when the Todo was saved.
  onAdd: (title: string) => Promise<boolean>
}

export function TodoForm({ onAdd }: TodoFormProps) {
  const [title, setTitle] = useState('')
  const trimmed = title.trim()

  return (
    <form
      className="todo-form"
      onSubmit={async (e) => {
        e.preventDefault()
        if (!trimmed) return
        // Keep the text when the request fails, so the user can retry.
        if (await onAdd(trimmed)) setTitle('')
      }}
    >
      <input
        aria-label="New todo"
        placeholder="What needs to be done?"
        maxLength={100}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <button type="submit" disabled={!trimmed}>
        Add
      </button>
    </form>
  )
}
