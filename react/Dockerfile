FROM node:26.13.1-bookworm-slim

RUN npm install --global pnpm@12.20.0
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm check && pnpm build

EXPOSE 5173
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
