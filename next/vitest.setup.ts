import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Remove rendered components after each test,
// so one test cannot see the DOM of another.
afterEach(() => {
  cleanup();
});
