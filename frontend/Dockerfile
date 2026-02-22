# Frontend — Next.js 14, TypeScript strict mode, Tailwind CSS
# All source files must be .ts or .tsx — no .js or .jsx
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
