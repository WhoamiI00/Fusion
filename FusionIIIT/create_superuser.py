import os
import sys
import django
import datetime

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")
django.setup()

# Import Django models and database connection
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.utils import timezone

# Create superuser using raw SQL to bypass ORM constraints
try:
    # Check if user already exists
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user WHERE username = 'admin'")
        user_exists = cursor.fetchone()[0] > 0
        
        if not user_exists:
            # Generate hashed password
            hashed_password = make_password('admin123')
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert user with all required fields including last_login
            cursor.execute("""
                INSERT INTO auth_user 
                (username, first_name, last_name, email, password, is_superuser, is_staff, is_active, date_joined, last_login) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                'admin',           # username
                '',                # first_name
                '',                # last_name
                'admin@example.com', # email
                hashed_password,   # password
                1,                 # is_superuser
                1,                 # is_staff
                1,                 # is_active
                now,               # date_joined
                now                # last_login
            ])
            print("Superuser 'admin' created successfully!")
        else:
            print("Superuser 'admin' already exists.")
            
except Exception as e:
    print(f"Error creating superuser: {e}")