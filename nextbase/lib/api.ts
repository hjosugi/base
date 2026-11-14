// Typed helper for the Todo API (the FastAPI app in ../fastapibase).
// The same functions work in Server Components and in the browser.

export type Todo = {
  id: number;
  title: string;
  done: boolean;
  /** ISO 8601 datetime, for example "2026-01-31T09:00:00Z". */
  created_at: string;
};

/** Body of POST /todos. */
export type TodoCreate = {
  title: string;
  done?: boolean;
};

/** Body of PATCH /todos/{id}. Send only the fields you want to change. */
export type TodoUpdate = {
  title?: string;
  done?: boolean;
};

/** The API answered, but with an error status (4xx or 5xx). */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// Keep this default the same as the one in next.config.ts.
const DEFAULT_API_URL = "http://127.0.0.1:8000";

function baseUrl(): string {
  // On the server we call the backend directly.
  if (typeof window === "undefined") {
    return process.env.API_URL ?? DEFAULT_API_URL;
  }
  // In the browser we call this Next.js server.
  // The rewrite in next.config.ts forwards /api/* to the backend.
  return "/api";
}

async function errorMessage(res: Response): Promise<string> {
  // FastAPI puts the reason in "detail". It is a string for 404
  // and a list of problems for 422.
  const body: unknown = await res.json().catch(() => null);
  if (
    typeof body === "object" &&
    body !== null &&
    "detail" in body &&
    typeof body.detail === "string"
  ) {
    return body.detail;
  }
  return `API error: ${res.status} ${res.statusText}`.trim();
}

// If the API cannot be reached at all, fetch() rejects with a TypeError.
async function request(path: string, init?: RequestInit): Promise<Response> {
  const res = await fetch(`${baseUrl()}${path}`, {
    ...init,
    // Always ask the API. Do not reuse a cached response.
    cache: "no-store",
  });
  if (!res.ok) {
    throw new ApiError(res.status, await errorMessage(res));
  }
  return res;
}

function jsonBody(data: unknown): RequestInit {
  return {
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  };
}

// The `as` casts below trust the API to return the documented shape.
// Nothing checks it at runtime.

export async function listTodos(): Promise<Todo[]> {
  const res = await request("/todos");
  return (await res.json()) as Todo[];
}

export async function createTodo(input: TodoCreate): Promise<Todo> {
  const res = await request("/todos", { method: "POST", ...jsonBody(input) });
  return (await res.json()) as Todo;
}

export async function updateTodo(id: number, input: TodoUpdate): Promise<Todo> {
  const res = await request(`/todos/${id}`, {
    method: "PATCH",
    ...jsonBody(input),
  });
  return (await res.json()) as Todo;
}

export async function deleteTodo(id: number): Promise<void> {
  // 204 No Content: there is no body to read.
  await request(`/todos/${id}`, { method: "DELETE" });
}
