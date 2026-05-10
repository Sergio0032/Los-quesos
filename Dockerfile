# 1. Usar la imagen de Python ligera y oficial
FROM python:3.11-slim

# 2. Carpeta de trabajo interna
WORKDIR /app

# 3. Copiar dependencias e instalarlas (Separado para mayor velocidad)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar SOLO el motor de tu Worker y la configuración
COPY src/ ./src/
COPY config.py .

# 5. La orden MAESTRA: Ejecuta todos tus scripts en orden de izquierda a derecha. 
# (El símbolo && asegura que el siguiente script solo empiece si el anterior terminó bien). 
CMD ["sh", "-c", "python src/download_partidos.py && python src/download_clasificaciones.py && python src/download_jugadores.py && python src/download_fifa.py && python src/clean_fifa.py"]