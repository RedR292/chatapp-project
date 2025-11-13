
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
COPY --from=build /app/dist /usr/share/nginx/html

# Add script snippet to /app/dist/index.html
RUN echo "\
    <script> \
    var ws = null; \
    function connect(event) { \
        var client_id = Date.now() \
        document.querySelector('#client-id').textContent = client_id; \
        document.querySelector('#room-id').textContent = channelId.value; \
        if (ws) ws.close() \
        ws = new WebSocket(`wss://xxx-du.a.run.app/ws/${channelId.value}/${client_id}`); \
        ws.onmessage = function(event) { \
            var messages = document.getElementById('messages') \
            var message = document.createElement('li') \
            var content = document.createTextNode(event.data) \
            message.appendChild(content) \
            messages.appendChild(message) \
        }; \
        event.preventDefault() \
    } \
    function sendMessage(event) { \
        var input = document.getElementById('messageText') \
        ws.send(input.value) \
        input.value = '' \
        event.preventDefault() \
        document.getElementById('messageText').focus() \
    } \
</script>' | sed -i '13i' '/usr/share/nginx/html/index.html'

# Copy custom nginx configuration (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for Cloud Run
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
