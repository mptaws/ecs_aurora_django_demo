#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
#python manage.py runserver 0.0.0.0:8000
gunicorn todo_project.wsgi:application --bind 0.0.0.0:8000