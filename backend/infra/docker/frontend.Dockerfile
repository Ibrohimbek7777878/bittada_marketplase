# Frontend image — used in prod only. In dev, run `make frontend-dev`.
FROM node:20-alpine AS build
WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY infra/docker/nginx/frontend.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
