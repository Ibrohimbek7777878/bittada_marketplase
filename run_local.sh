#!/bin/bash
# Bittada — Local Django Development Script
# Frontend: Django Templates (no Vite, no SPA)

set -e

cd "$(dirname "$0")/backend"

echo "=========================================="
echo "  Bittada — Django Local Development"
echo "  Frontend: Django Templates"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Please install Python 3.12+"
    exit 1
fi

echo "✅ Python: $(python3 --version)"

# Create virtual environment if not exists
if [ ! -d "../.venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv ../.venv
fi

# Activate virtual environment
source ../.venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip

# Install requirements if exists
if [ -f "requirements/base.txt" ]; then
    pip install -q -r requirements/base.txt
elif [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
fi

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --run-syncdb

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Create superuser if no users exist
echo "👤 Checking admin user..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
import django
django.setup()
from apps.users.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@bittada.uz', 'admin123')
    print('✅ Created superuser: admin / admin123')
else:
    print('✅ Admin user exists')
" 2>/dev/null || true

echo ""
echo "=========================================="
echo "  🚀 Starting Django Development Server"
echo "=========================================="
echo ""
echo "  📍 URL: http://127.0.0.1:8000"
echo "  👤 Admin: http://127.0.0.1:8000/admin"
echo "     Login: admin / admin123"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

# Run server
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py runserver 0.0.0.0:8000
