#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Compile static assets
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser automatically if it doesn't exist
python -c "
import os
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('Superuser created successfully!')
else:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print('Superuser password updated successfully!')
"
