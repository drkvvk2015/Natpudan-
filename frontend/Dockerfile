# Build stage (Mirrored for corporate bypass)
FROM mirror.gcr.io/library/node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Handle corporate proxy during build
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG http_proxy
ARG https_proxy

# Install dependencies
RUN npm config set strict-ssl false && npm install --production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM mirror.gcr.io/library/nginx:alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
