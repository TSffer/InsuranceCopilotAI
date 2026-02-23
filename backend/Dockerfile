# Usamos una imagen ligera de Python
FROM python:3.12-slim

# Instalamos uv para una gestión de dependencias ultra rápida
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Instalamos dependencias del sistema necesarias para psycopg y otras librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos archivos de dependencias e instalamos
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev

# Copiamos el resto del código
COPY . .

# Exponemos el puerto 8000 (ajustar en Azure Container App Ingress)
EXPOSE 8000

# Comando de arranque usando run.py como pidió el usuario
# Aseguramos que run.py use 0.0.0.0 internamente
CMD ["uv", "run", "python", "run.py"]
