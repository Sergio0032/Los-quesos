FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config.py .

CMD ["sh", "-c", "python src/download_partidos.py && python src/download_clasificaciones.py && python src/download_jugadores.py && python src/download_fifa.py && python src/clean_fifa.py"]