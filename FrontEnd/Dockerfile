
# BUILD Next.js
FROM node:20-alpine

WORKDIR /frontend_app

# Copiar dependencias
COPY package.json package-lock.json ./
RUN npm install

# Copiar config (CRÍTICO para CSS)
COPY next.config.ts ./next.config.ts
COPY postcss.config.mjs ./postcss.config.mjs
COPY tsconfig.json ./tsconfig.json

# Copiar código
COPY app ./app
COPY public ./public

# Build Next
RUN npm run build

# Exponer puerto
EXPOSE 3000

# Ejecutar Next
CMD ["npm", "start"]




