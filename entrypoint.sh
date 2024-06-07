#!/bin/bash

# Este script comprueba si la variable de entorno RUN_TESTS está establecida a "true".
# Si es así, ejecuta las pruebas; de lo contrario, inicia la aplicación.

if [ "$RUN_TESTS" = "true" ]; then
    echo "Running Tests..."
    pytest /service/src/test/
else
    echo "Starting Application..."
    uvicorn main_api:app --host 0.0.0.0 --port 10000
fi