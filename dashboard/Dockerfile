FROM node:slim AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN apt update && apt install -y openssl
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 app
RUN adduser --system --uid 1001 app
RUN mkdir .next
RUN chown app:app .next
COPY --from=builder --chown=app:app /app/.next/standalone ./
COPY --from=builder --chown=app:app /app/.next/static ./.next/static
COPY --from=builder --chown=app:app /app/public ./public
USER nextjs

EXPOSE 3000

ENV PORT 3000
# set hostname to localhost
ENV HOSTNAME 0.0.0.0

# Expose environment variable for runtime configuration
# Users can override this by setting NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL
ENV NEXT_PUBLIC_EXOSPHERE_STATE_MANAGER_URL=http://localhost:8000
ENV NEXT_PUBLIC_DEV_MODE=true

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/next-config-js/output
CMD ["node", "server.js"]
