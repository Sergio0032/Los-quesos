# Usamos una versión ligera de Python
FROM python:3.11-slim

# Definimos la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de librerías y las instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo tu código al contenedor
COPY . .

# Exponemos el puerto de tu aplicación web
EXPOSE 8501

# Comando para arrancar tu menú principal (ajustado a tu carpeta 'web')
CMD ["streamlit", "run", "web/MENÚ.py", "--server.address=0.0.0.0"]

#FROM: Eliges los ingredientes base (Python).

#WORKDIR: Eliges en qué encimera vas a cocinar (/app).

#RUN: Preparas los ingredientes (instalas las librerías).

#COPY: Metes tu código en la olla.

#CMD: Enciendes el fuego (ejecutas el programa).