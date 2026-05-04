#!/bin/bash
# Start both backend and frontend on a SINGLE port (8000)
# Django serves both the API and the frontend SPA

set -e

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python not found!"
    exit 1
fi

echo "🚀 Starting Bittada on single port (8000)..."
echo ""

# Check if frontend is built
if [ ! -f "frontend/dist/index.html" ]; then
    echo "⚠️  Frontend not built. Building now..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "✅ Frontend built successfully!"
    echo ""
fi

# Check if database is migrated
echo "📦 Checking database migrations..."
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

$PYTHON manage.py migrate --no-input
echo ""

# Create superuser if not exists
echo "👤 Checking for superuser..."
$PYTHON manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('⚠️  No superuser found. Create one with: python manage.py createsuperuser')
else:
    print('✅ Superuser exists')
"
echo ""

# Start Django server (serves both API and frontend)
echo "🌐 Starting Django server on http://localhost:8000"
echo "   - API:      http://localhost:8000/api/v1/"
echo "   - API Docs: http://localhost:8000/api/docs/"
echo "   - Admin:    http://localhost:8000/admin/"
echo "   - Frontend: http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

$PYTHON manage.py runserver 8000
