#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Auto-setting up production environment..."
python manage.py auto_setup

echo "Build completed successfully!"
echo "Little Lemon Restaurant is ready!"
echo "Admin login: admin/admin123"
echo "Demo login: demo/demo123"# exit on error
set -o errexit

echo "🔄 Installing Python dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "� Auto-setting up production environment..."
python manage.py auto_setup

echo "✅ Build completed successfully!"
echo "🌐 Little Lemon Restaurant is ready!"
echo "👨‍💼 Admin login: admin/admin123"
echo "👤 Demo login: demo/demo123"