#!/bin/bash

# Salir inmediatamente si un comando falla
set -e

# Ruta al archivo docker-compose.yml
COMPOSE_FILE="docker-compose.yml"

# Asegurarse de que los contenedores de una ejecución previa estén abajo (especialmente test_db)
echo "Asegurando que los contenedores de test previos estén detenidos..."
docker-compose -f "${COMPOSE_FILE}" down --remove-orphans # Elimina huérfanos también

echo "Levantando la base de datos de prueba (test_db)..."
docker-compose -f "${COMPOSE_FILE}" up -d test_db

# Esperar a que PostgreSQL en test_db esté listo
echo "Esperando a que la base de datos de prueba (test_db) esté disponible..."
MAX_RETRIES=12 # Intentar por 60 segundos (12 * 5s)
CURRENT_RETRY=0
DB_READY=false

while [ ${CURRENT_RETRY} -lt ${MAX_RETRIES} ]; do
    # Usar las credenciales y BD por defecto que definimos en docker-compose.yml para test_db
    # (testuser, testpassword, app_test) y el puerto expuesto (5433)
    if docker-compose -f "${COMPOSE_FILE}" exec -T test_db pg_isready -U testuser -d app_test -h localhost -p 5432; then
        DB_READY=true
        break
    fi
    echo "Esperando... intento $((CURRENT_RETRY + 1))/${MAX_RETRIES}"
    sleep 5
    CURRENT_RETRY=$((CURRENT_RETRY + 1))
done

if [ "$DB_READY" = "false" ]; then
    echo "La base de datos de prueba no estuvo lista a tiempo."
    echo "Logs del contenedor test_db:"
    docker-compose -f "${COMPOSE_FILE}" logs test_db
    docker-compose -f "${COMPOSE_FILE}" down # Limpiar
    exit 1
fi
echo "Base de datos de prueba lista."

# (Opcional) Aquí podrías añadir pasos para construir o levantar el servicio 'api'
# si tus tests E2E lo requieren y necesitan que la API use la test_db.
# Por ejemplo:
# echo "Construyendo y levantando el servicio api para tests E2E..."
# docker-compose -f "${COMPOSE_FILE}" up -d --build api
# Y asegurar que esta 'api' use TEST_DATABASE_URL.

echo "Ejecutando tests..."
# Asume que pytest está en el PATH y que tu virtualenv está activado si usas uno.
# Los tests se conectarán a test_db en localhost:5433 según tests/conftest.py
pytest "$@"

TEST_EXIT_CODE=$?

echo "Tests finalizados. Código de salida: $TEST_EXIT_CODE"

echo "Deteniendo y eliminando contenedores de test..."
docker-compose -f "${COMPOSE_FILE}" down --remove-orphans

exit $TEST_EXIT_CODE
