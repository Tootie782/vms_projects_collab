#!/bin/bash

# Comprueba si la variable RUN_TESTS está configurada a "true"
if [ "$RUN_TESTS" = "true" ]; then
    echo "Running Tests..."
    # Comando para ejecutar pruebas, ajusta según sea necesario
    cd /service
    pytest src/test/test_api.py
else
    echo "Running Application..."
    # Inicia la aplicación, pasa todos los argumentos a Uvicorn
    exec "$@"
fi
