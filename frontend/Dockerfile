FROM node:24-alpine AS build

WORKDIR /app

ARG NPM_CONFIG_REGISTRY=https://registry.npmmirror.com

COPY package*.json ./
RUN npm ci --registry=$NPM_CONFIG_REGISTRY

COPY . .

ARG VITE_API_BASE_URL=/dify/api
ARG VITE_APP_BASE_PATH=/dify/
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_BASE_PATH=$VITE_APP_BASE_PATH

RUN npm run build

FROM nginx:1.29-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html/dify

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --spider -q http://127.0.0.1/dify/ || exit 1
