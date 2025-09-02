FROM node:slim AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN apt-get update && apt-get install -y --no-install-recommends openssl
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
USER app

EXPOSE 3000

ENV PORT=3000
# set hostname to localhost
ENV HOSTNAME=0.0.0.0

# Expose environment variables for runtime configuration
# Users can override these by setting the corresponding environment variables
# 
# SECURITY: This container uses server-side rendering (SSR) for enhanced security
# - EXOSPHERE_API_KEY is handled server-side and never exposed to browser
# - All API calls go through secure Next.js API routes
# - Production-ready security architecture
ENV EXOSPHERE_STATE_MANAGER_URI=http://localhost:8000
ENV EXOSPHERE_API_KEY=exosphere@123
ENV NEXT_PUBLIC_DEFAULT_NAMESPACE=default

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/next-config-js/output
CMD ["node", "server.js"]
