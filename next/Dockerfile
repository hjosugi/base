FROM node:26.13.1-bookworm-slim AS build

RUN npm install --global pnpm@12.20.0
WORKDIR /app
ARG API_URL=http://fastapi:8000
ENV API_URL=$API_URL
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm check && pnpm build

FROM node:26.13.1-bookworm-slim AS runtime

RUN npm install --global pnpm@12.20.0
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app ./
USER node
EXPOSE 3000
CMD ["pnpm", "start", "--hostname", "0.0.0.0"]
