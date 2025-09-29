#Versión de Python que vamos a usar
FROM python:3.13.5-slim

#Establecemos el directorio de trabajo
WORKDIR /app

#Copiamos la lista de dependencias
COPY requirements.txt .

#Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt
