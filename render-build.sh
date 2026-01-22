#!/usr/bin/env bash
echo ">>> Ejecutando collectstatic..."
python manage.py collectstatic --noinput
