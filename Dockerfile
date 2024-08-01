# Utiliza una imagen base de Python 3.12
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de dependencias y el código de la aplicación
COPY requirements.txt requirements.txt
COPY . .

# Instala las dependencias
RUN pip3 install --no-cache-dir -r requirements.txt

# Define el comando por defecto para ejecutar la aplicación
CMD ["gunicorn", "-w", "4", "wsgi:app"]