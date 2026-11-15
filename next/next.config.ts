import type { NextConfig } from "next";

// Origin of the backend API. Set API_URL in .env.local to change it.
// Keep this default the same as the one in lib/api.ts.
const apiUrl = process.env.API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  // The browser only talks to this Next.js server.
  // A request to /api/todos is forwarded to <API_URL>/todos.
  // So the backend needs no CORS setup.
  rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
