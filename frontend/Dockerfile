# Etapa 1: Construcción (Actualizado a Node 22 para compatibilidad con Vite)
FROM node:22-alpine AS build

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar código fuente
COPY . .

# Construir la aplicación
RUN npm run build

# Etapa 2: Servir con Nginx
FROM nginx:alpine

# Copiar la configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos construidos
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer puerto
EXPOSE 80

# Comando para ejecutar Nginx
CMD ["nginx", "-g", "daemon off;"]