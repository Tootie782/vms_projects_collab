FROM python:3.9

EXPOSE 10000

WORKDIR /service

# Copia todo el proyecto al directorio de trabajo (incluidos los tests)
COPY . ./

# Instala las dependencias
RUN pip install -r dependences.txt

# Script de entrada que puede ejecutar la aplicación o correr pruebas
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
CMD ["uvicorn", "main_api:app", "--port", "10000", "--host", "0.0.0.0"]
