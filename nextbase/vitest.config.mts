import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    // Resolve the "@/..." imports from tsconfig.json.
    tsconfigPaths: true,
  },
  test: {
    // A browser-like DOM, so components can render in Node.js.
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
  },
});
