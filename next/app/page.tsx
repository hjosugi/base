import { Suspense } from "react";
import { ApiUnavailable } from "@/components/api-unavailable";
import { TodoApp } from "@/components/todo-app";
import { listTodos, type Todo } from "@/lib/api";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-xl flex-1 px-6 py-16">
      <h1 className="text-2xl font-semibold">Todos</h1>
      {/* Everything outside <Suspense> is the static shell.
          The list needs fresh data, so it is rendered on every request. */}
      <Suspense fallback={<p className="mt-6 text-zinc-500">Loading...</p>}>
        <TodoList />
      </Suspense>
    </main>
  );
}

// A Server Component: it runs only on the server and fetches from the backend.
async function TodoList() {
  let todos: Todo[];
  try {
    todos = await listTodos();
  } catch (error) {
    // fetch() rejects with a TypeError when it cannot connect.
    if (error instanceof TypeError) {
      return <ApiUnavailable />;
    }
    // Any other error is a real problem. Do not hide it.
    throw error;
  }
  return <TodoApp initialTodos={todos} />;
}
