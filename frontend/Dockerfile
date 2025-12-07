# 🏗 Stage 1 — Build
FROM node:18.20.3-alpine AS builder

WORKDIR /app

RUN apk add --no-cache libc6-compat

COPY package*.json ./
RUN npm ci --omit=optional

ARG NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE

COPY . .

RUN npm run build


# 🚀 Stage 2 — Production runtime
FROM node:18.20.3-alpine AS runner

WORKDIR /app


#Set runtime environment variables
# Set the port the container will listen on. This matches your package.json (3000)

ENV NODE_ENV=production
ENV PORT=3000

# Disable Next.js telemetry reporting
ENV NEXT_TELEMETRY_DISABLED=1

RUN apk add --no-cache libc6-compat

# Create a non-root user
RUN addgroup -g 1001 nodejs \
    && adduser -S -u 1001 nextjs -G nodejs

# Copy artifacts
#COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Switch to non-root user
USER nextjs

EXPOSE 3000
CMD ["npm", "start"]
