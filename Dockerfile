# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/places data/facebook data/youtube data/twitter data/news

# Exponer el puerto para FastAPI
EXPOSE 8000

# Establecer variables de entorno por defecto
ENV PYTHONUNBUFFERED=1

# Script de inicio
COPY start.sh .
RUN chmod +x start.sh

# Comando para ejecutar la aplicación
CMD ["./start.sh"]