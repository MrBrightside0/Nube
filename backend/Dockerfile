# Imagen base de Python
FROM python:3.13.5-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Configurar variable de entorno para Railway (usa el puerto asignado)
ENV PORT=5000

# Exponer puerto dinámico (Railway lo reemplaza con $PORT)
EXPOSE $PORT

# Comando para correr Flask
CMD ["python", "Nube.py"]
