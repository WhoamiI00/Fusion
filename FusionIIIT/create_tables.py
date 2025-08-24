import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fusion.settings.development')
django.setup()

# Import necessary models
from django.db import connection

# Create tables for programme_curriculum app
with connection.cursor() as cursor:
    # Create Batch table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programme_curriculum_batch (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        year INTEGER NOT NULL,
        running_batch BOOLEAN NOT NULL,
        curriculum_id INTEGER NULL,
        discipline_id INTEGER NOT NULL,
        FOREIGN KEY (curriculum_id) REFERENCES programme_curriculum_curriculum(id),
        FOREIGN KEY (discipline_id) REFERENCES programme_curriculum_discipline(id)
    )
    """)
    
    # Create Programme table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programme_curriculum_programme (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category VARCHAR(3) NOT NULL,
        name VARCHAR(70) NOT NULL UNIQUE,
        programme_begin_year INTEGER NOT NULL
    )
    """)
    
    # Create Discipline table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programme_curriculum_discipline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL UNIQUE,
        acronym VARCHAR(10) NOT NULL
    )
    """)
    
    # Create Discipline-Programme many-to-many relationship table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programme_curriculum_discipline_programmes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discipline_id INTEGER NOT NULL,
        programme_id INTEGER NOT NULL,
        FOREIGN KEY (discipline_id) REFERENCES programme_curriculum_discipline(id),
        FOREIGN KEY (programme_id) REFERENCES programme_curriculum_programme(id),
        UNIQUE(discipline_id, programme_id)
    )
    """)
    
    # Create Curriculum table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programme_curriculum_curriculum (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        version DECIMAL(5,1) NOT NULL,
        working_curriculum BOOLEAN NOT NULL,
        no_of_semester INTEGER NOT NULL,
        min_credit INTEGER NOT NULL,
        latest_version BOOLEAN NOT NULL,
        programme_id INTEGER NOT NULL,
        FOREIGN KEY (programme_id) REFERENCES programme_curriculum_programme(id),
        UNIQUE(name, version)
    )
    """)

print("Tables created successfully!")