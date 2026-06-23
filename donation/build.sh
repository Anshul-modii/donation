#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Compile static assets
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
