// Shown instead of the Todo list when the backend cannot be reached.
export function ApiUnavailable() {
  return (
    <div
      role="alert"
      className="mt-6 rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100"
    >
      <p className="font-semibold">The API is not reachable.</p>
      <p className="mt-2">Start the backend, then reload this page:</p>
      <pre className="mt-2 overflow-x-auto rounded bg-black/10 p-2 font-mono dark:bg-white/10">
        cd ../fastapi &amp;&amp; uv run fastapi dev
      </pre>
      <p className="mt-2">
        The API address comes from <code className="font-mono">API_URL</code> in{" "}
        <code className="font-mono">.env.local</code>. The default is{" "}
        <code className="font-mono">http://127.0.0.1:8000</code>.
      </p>
    </div>
  );
}
