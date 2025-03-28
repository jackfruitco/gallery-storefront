#!/bin/bash

# Collect static files
echo "Collecting static files..."
python src/manage.py collectstatic -v 1 --no-input

# Apply database migrations
echo
echo "Applying database migrations..."
python src/manage.py migrate

# Start server
echo
echo "Starting server..."
python src/manage.py runserver 0.0.0.0:8000
