import os
import sys
import django

# Add backend to sys.path
sys.path.append('/home/ibrohim/Desktop/client_baza/bittada_marketplase_Eski/backend')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.forms import UserUpdateForm, ProfileUpdateForm
print("Forms imported successfully!")
