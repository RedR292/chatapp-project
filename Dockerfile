
# ---- Build stage ----
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy all source files
COPY . .

# Build the React app for production
RUN npm run build

# ---- Run stage ----
FROM nginx:alpine

# Copy built static files from previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration (optional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080 for Cloud Run
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
