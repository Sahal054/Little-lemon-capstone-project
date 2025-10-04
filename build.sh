#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔄 Installing Python dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "🏪 Setting up restaurant configuration..."
python manage.py setup_restaurant

echo "✅ Build completed successfully!"