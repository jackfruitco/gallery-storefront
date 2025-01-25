#!/bin/bash

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic -v 1 --no-input

# Apply database migrations
echo
echo "Applying database migrations..."
python manage.py migrate

# Start server
echo
echo "Starting server..."
gunicorn GalleryStorefront.wsgi:application --bind=0.0.0.0:8000