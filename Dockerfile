# Usar Python 3.12 como imagen base
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Evitar que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Asegurar que la salida de Python se envía directamente a la terminal
ENV PYTHONUNBUFFERED=1

# Instalar UV para gestión de dependencias
RUN pip install --no-cache-dir uv

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias con UV
RUN uv pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto que usa la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]