#!/usr/bin/env bash
# Script usado por Render para recopilar archivos estáticos

echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput
