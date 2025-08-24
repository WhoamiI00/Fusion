import os
import sys
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")
django.setup()

# Import Django models and database connection
from django.db import connection

# Create django_site table and insert default site
try:
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='django_site';
        """)
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create the django_site table
            cursor.execute("""
                CREATE TABLE django_site (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain VARCHAR(100) NOT NULL,
                    name VARCHAR(50) NOT NULL
                );
            """)
            print("Created django_site table")
            
            # Insert default site
            cursor.execute("""
                INSERT INTO django_site (id, domain, name)
                VALUES (1, 'example.com', 'example.com');
            """)
            print("Inserted default site")
        else:
            print("django_site table already exists")
            
        # Check if content type table exists and has entries
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='django_content_type';
        """)
        content_type_exists = cursor.fetchone() is not None
        
        if content_type_exists:
            # Check if there are entries
            cursor.execute("SELECT COUNT(*) FROM django_content_type;")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert basic content types
                cursor.execute("""
                    INSERT INTO django_content_type (app_label, model, name)
                    VALUES ('auth', 'user', 'user');
                """)
                print("Inserted basic content types")
            else:
                print(f"django_content_type table has {count} entries")
        else:
            print("django_content_type table does not exist")
            
except Exception as e:
    print(f"Error: {e}")