
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

# Add script snippet to /app/dist/index.html
RUN cat /app/script.txt | sed -i '13i' /app/dist/index.html

# Copy built static files from previous stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for Cloud Run
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
