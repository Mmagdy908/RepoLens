FROM node:20-alpine

WORKDIR /app

# Install dependencies at build time (cached layer)
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Copy source (overridden by bind-mount in dev)
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
