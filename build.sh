#!/usr/bin/env bash
# Exit on error
set -o errexit

# Crear un superusuario automáticamente
echo "from django.contrib.auth import get_user_model; \
      User = get_user_model(); \
      User.objects.filter(username='admin').exists() or \
      User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" | python manage.py shell
