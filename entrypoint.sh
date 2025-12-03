#!/bin/sh

# Wait for PostgreSQL to be ready
python wait_for_db.py

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if not exists
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || true
fi

# Start Gunicorn
exec gunicorn portfolio.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2
