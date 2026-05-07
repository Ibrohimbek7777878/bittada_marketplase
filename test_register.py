import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import RequestFactory
from apps.products.views import register_view

rf = RequestFactory()
request = rf.post('/register/', {
    'first_name': 'Test User',
    'username': 'testuser123',
    'email': 'test12345@example.com',
    'phone': '+998901234567',
    'password': 'Password123!',
    'role': 'customer',
    'account_type': 'individual',
})
response = register_view(request)
print("Status:", response.status_code)
print("Content:", response.content)
