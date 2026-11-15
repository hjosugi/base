import react from '@vitejs/plugin-react'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // API_URL comes from the shell or from a .env file. See .env.example.
  const env = loadEnv(mode, process.cwd(), '')
  const apiUrl = env.API_URL || 'http://127.0.0.1:8000'

  return {
    plugins: [react()],
    server: {
      proxy: {
        // The browser calls /api/todos. The dev server sends it on to
        // http://127.0.0.1:8000/todos. The browser only talks to one origin,
        // so the backend needs no CORS setup.
        '/api': {
          target: apiUrl,
          changeOrigin: true,
          ws: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
    },
  }
})
