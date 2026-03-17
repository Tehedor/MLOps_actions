# GitHub Container Registry (GHCR)
# Usamos una versión ligera de Python 3.11
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y fuerza a que la salida de consola no tenga buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos 'make' a nivel de sistema operativo (ya que lo usas mucho en tu pipeline)
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /workspace

# Copiamos solo el archivo de requerimientos primero (para aprovechar la caché de Docker)
COPY requirements2-mlops.txt .

# Instalamos las dependencias GLOBALMENTE (en un contenedor no hace falta .venv)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements2-mlops.txt

# El comando por defecto al arrancar el contenedor será bash
CMD ["/bin/bash"]



# docker build -f .mlops_tools/github_container_job/Dockerfile -t test-env .
# docker run -it --rm test-env /bin/bash