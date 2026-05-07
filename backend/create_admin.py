from apps.users.models import User
try:
    if not User.objects.filter(username='admin_new').exists():
        User.objects.create_superuser('admin_new', 'admin@example.com', 'admin123456')
        print("SUCCESS: Superuser 'admin_new' created.")
    else:
        print("INFO: Superuser 'admin_new' already exists.")
except Exception as e:
    print(f"ERROR: {e}")
