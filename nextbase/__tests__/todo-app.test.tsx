import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";
import { TodoApp } from "@/components/todo-app";
import { createTodo, deleteTodo, updateTodo, type Todo } from "@/lib/api";

// Replace the API helper with fakes. The component is tested without a server.
vi.mock("@/lib/api");

const milk: Todo = {
  id: 1,
  title: "Buy milk",
  done: false,
  created_at: "2026-01-31T09:00:00Z",
};

beforeEach(() => {
  vi.resetAllMocks();
});

test("shows the todos from the server", () => {
  render(<TodoApp initialTodos={[milk]} />);

  expect(screen.getByRole("checkbox", { name: "Buy milk" })).toBeDefined();
});

test("shows a hint when there are no todos", () => {
  render(<TodoApp initialTodos={[]} />);

  expect(screen.getByText("No todos yet.")).toBeDefined();
});

test("adds a todo", async () => {
  vi.mocked(createTodo).mockResolvedValue({ ...milk, id: 2, title: "Walk" });
  render(<TodoApp initialTodos={[milk]} />);

  fireEvent.change(screen.getByRole("textbox", { name: "New todo" }), {
    target: { value: "  Walk  " },
  });
  fireEvent.click(screen.getByRole("button", { name: "Add" }));

  // findBy... waits until the new item is on the screen.
  expect(await screen.findByRole("checkbox", { name: "Walk" })).toBeDefined();
  // The title is trimmed before it is sent.
  expect(createTodo).toHaveBeenCalledWith({ title: "Walk" });
});

test("does not call the API for an empty title", () => {
  render(<TodoApp initialTodos={[]} />);

  fireEvent.click(screen.getByRole("button", { name: "Add" }));

  expect(createTodo).not.toHaveBeenCalled();
});

test("toggles done", async () => {
  vi.mocked(updateTodo).mockResolvedValue({ ...milk, done: true });
  render(<TodoApp initialTodos={[milk]} />);

  fireEvent.click(screen.getByRole("checkbox", { name: "Buy milk" }));

  expect(
    await screen.findByRole("checkbox", { name: "Buy milk", checked: true }),
  ).toBeDefined();
  expect(updateTodo).toHaveBeenCalledWith(1, { done: true });
});

test("deletes a todo", async () => {
  vi.mocked(deleteTodo).mockResolvedValue();
  render(<TodoApp initialTodos={[milk]} />);

  fireEvent.click(screen.getByRole("button", { name: "Delete Buy milk" }));

  expect(await screen.findByText("No todos yet.")).toBeDefined();
  expect(deleteTodo).toHaveBeenCalledWith(1);
});

test("shows the reason when the API call fails", async () => {
  vi.mocked(deleteTodo).mockRejectedValue(new Error("Todo 1 not found"));
  render(<TodoApp initialTodos={[milk]} />);

  fireEvent.click(screen.getByRole("button", { name: "Delete Buy milk" }));

  const alert = await screen.findByRole("alert");
  expect(alert.textContent).toBe("Todo 1 not found");
  // The todo stays in the list.
  expect(screen.getByRole("checkbox", { name: "Buy milk" })).toBeDefined();
});
