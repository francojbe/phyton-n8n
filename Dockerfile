# Usar la imagen oficial de Playwright con Python preinstalado
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY main.py .

# Ya que usamos la imagen oficial de Playwright, los navegadores ya están instalados.
# Sin embargo, nos aseguramos de que estén listos para el runtime
RUN playwright install chromium

# Exponer el puerto del microservicio
EXPOSE 8000

# Comando para iniciar el servicio con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
