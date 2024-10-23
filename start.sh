#!/bin/bash

# Iniciar el servidor FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Esperar un momento para que FastAPI inicie
sleep 5

# Iniciar el orchestrator
python -m core.orchestrator