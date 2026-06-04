FROM nginx:1.27-alpine

# Reemplaza la configuración por defecto de Nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia la interfaz web al directorio que Nginx sirve
COPY html/ /usr/share/nginx/html/

EXPOSE 80

# Verificación de salud del contenedor
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/frontend-health || exit 1
