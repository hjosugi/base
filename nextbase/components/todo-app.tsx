"use client";

import { useState, type SubmitEvent } from "react";
import { createTodo, deleteTodo, updateTodo, type Todo } from "@/lib/api";

// The server renders the first list and passes it as `initialTodos`.
// After that, this component keeps the list in state and calls the API
// through /api/* (see lib/api.ts).
export function TodoApp({ initialTodos }: { initialTodos: Todo[] }) {
  const [todos, setTodos] = useState(initialTodos);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Run one API call. Show the reason if it fails.
  async function run(action: () => Promise<void>) {
    setError(null);
    try {
      await action();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    }
  }

  function handleAdd(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = title.trim();
    if (trimmed === "") return;
    void run(async () => {
      const created = await createTodo({ title: trimmed });
      setTodos((current) => [...current, created]);
      setTitle("");
    });
  }

  function handleToggle(todo: Todo) {
    void run(async () => {
      const updated = await updateTodo(todo.id, { done: !todo.done });
      setTodos((current) =>
        current.map((t) => (t.id === updated.id ? updated : t)),
      );
    });
  }

  function handleDelete(todo: Todo) {
    void run(async () => {
      await deleteTodo(todo.id);
      setTodos((current) => current.filter((t) => t.id !== todo.id));
    });
  }

  return (
    <section className="mt-6">
      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          aria-label="New todo"
          placeholder="What needs to be done?"
          maxLength={100}
          className="min-w-0 flex-1 rounded-md border border-zinc-300 bg-transparent px-3 py-2 dark:border-zinc-700"
        />
        <button
          type="submit"
          className="rounded-md bg-foreground px-4 py-2 font-medium text-background"
        >
          Add
        </button>
      </form>

      {error !== null && (
        <p role="alert" className="mt-3 text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}

      {todos.length === 0 ? (
        <p className="mt-6 text-zinc-500">No todos yet.</p>
      ) : (
        <ul className="mt-6 divide-y divide-zinc-200 dark:divide-zinc-800">
          {todos.map((todo) => (
            <li key={todo.id} className="flex items-center gap-3 py-2">
              <label className="flex min-w-0 flex-1 items-center gap-3">
                <input
                  type="checkbox"
                  checked={todo.done}
                  onChange={() => handleToggle(todo)}
                />
                <span
                  className={
                    todo.done
                      ? "truncate text-zinc-500 line-through"
                      : "truncate"
                  }
                >
                  {todo.title}
                </span>
              </label>
              <button
                type="button"
                onClick={() => handleDelete(todo)}
                aria-label={`Delete ${todo.title}`}
                className="rounded-md px-2 py-1 text-sm text-zinc-500 hover:text-red-600"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
