import './App.css'
import { TodoForm } from './components/TodoForm'
import { TodoList } from './components/TodoList'
import { useTodos } from './useTodos'

function App() {
  const { todos, status, error, live, reload, add, toggle, remove } = useTodos()
  const doneCount = todos.filter((t) => t.done).length

  return (
    <main>
      <header>
        <h1>React Todo</h1>
        <span
          className={live ? 'badge live' : 'badge'}
          title="Event stream (SSE)"
        >
          {live ? 'live' : 'offline'}
        </span>
      </header>

      <TodoForm onAdd={add} />

      {status === 'loading' && <p>Loading...</p>}

      {status === 'error' && (
        <section className="hint">
          <p>Cannot reach the API ({error}). Start the backend, then retry.</p>
          <pre>cd ../fastapi && uv run fastapi dev</pre>
          <button type="button" onClick={reload}>
            Retry
          </button>
        </section>
      )}

      {status === 'ready' && (
        <>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          <TodoList todos={todos} onToggle={toggle} onRemove={remove} />
          <p className="count">
            {doneCount} / {todos.length} done
          </p>
        </>
      )}
    </main>
  )
}

export default App
