import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import {
  ApiError,
  createTodo,
  deleteTodo,
  listTodos,
  updateTodo,
  type Todo,
} from "@/lib/api";

const todo: Todo = {
  id: 1,
  title: "Buy milk",
  done: false,
  created_at: "2026-01-31T09:00:00Z",
};

// A fake fetch. No test here talks to a real server.
const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  fetchMock.mockReset();
});

describe("in the browser", () => {
  test("listTodos gets /api/todos and returns the list", async () => {
    fetchMock.mockResolvedValue(Response.json([todo]));

    await expect(listTodos()).resolves.toEqual([todo]);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/todos",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  test("createTodo posts the title as JSON", async () => {
    fetchMock.mockResolvedValue(Response.json(todo, { status: 201 }));

    await expect(createTodo({ title: "Buy milk" })).resolves.toEqual(todo);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/todos",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "Buy milk" }),
      }),
    );
  });

  test("updateTodo patches one todo", async () => {
    fetchMock.mockResolvedValue(Response.json({ ...todo, done: true }));

    const updated = await updateTodo(1, { done: true });

    expect(updated.done).toBe(true);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/todos/1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ done: true }),
      }),
    );
  });

  test("deleteTodo accepts 204 with no body", async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }));

    await expect(deleteTodo(1)).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/todos/1",
      expect.objectContaining({ method: "DELETE" }),
    );
  });

  test("an error status becomes an ApiError with the API's detail", async () => {
    fetchMock.mockResolvedValue(
      Response.json({ detail: "Todo 9 not found" }, { status: 404 }),
    );

    const error = await deleteTodo(9).catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 404, message: "Todo 9 not found" });
  });

  test("an error without a JSON body uses the status line", async () => {
    // Next.js answers like this when the rewrite cannot reach the backend.
    fetchMock.mockResolvedValue(
      new Response("Internal Server Error", {
        status: 500,
        statusText: "Internal Server Error",
      }),
    );

    await expect(listTodos()).rejects.toThrow(
      "API error: 500 Internal Server Error",
    );
  });
});

describe("on the server", () => {
  beforeEach(() => {
    // Server code has no `window`.
    vi.stubGlobal("window", undefined);
  });

  test("listTodos calls the backend at API_URL", async () => {
    vi.stubEnv("API_URL", "http://backend.test:9000");
    fetchMock.mockResolvedValue(Response.json([]));

    await listTodos();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://backend.test:9000/todos",
      expect.anything(),
    );
  });

  test("the default backend is http://127.0.0.1:8000", async () => {
    vi.stubEnv("API_URL", undefined);
    fetchMock.mockResolvedValue(Response.json([]));

    await listTodos();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/todos",
      expect.anything(),
    );
  });
});
