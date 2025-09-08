import os
import sys
import django
import datetime

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")
django.setup()

# Import Django models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from applications.globals.models import ExtraInfo, DepartmentInfo, HoldsDesignation, Designation
from applications.academic_information.models import Student

# Create department if it doesn't exist
try:
    cse_dept = DepartmentInfo.objects.get(name="CSE")
    print("CSE department already exists")
except DepartmentInfo.DoesNotExist:
    cse_dept = DepartmentInfo.objects.create(name="CSE")
    print("Created CSE department")

# Create designation if it doesn't exist
try:
    student_desig = Designation.objects.get(name="student")
    print("Student designation already exists")
except Designation.DoesNotExist:
    student_desig = Designation.objects.create(
        name="student",
        full_name="Student",
        type="academic",
        category="student"
    )
    print("Created student designation")

# Create admin user if it doesn't exist
try:
    admin_user = User.objects.get(username="admin")
    print("Admin user already exists")
except User.DoesNotExist:
    admin_user = User.objects.create_superuser(
        username="admin",
        password="admin123",
        email="admin@example.com",
        first_name="Admin",
        last_name="User"
    )
    print("Created admin user")

# Create student user if it doesn't exist
try:
    student_user = User.objects.get(username="student")
    print("Student user already exists")
except User.DoesNotExist:
    student_user = User.objects.create_user(
        username="student",
        password="student123",
        email="student@example.com",
        first_name="Test",
        last_name="Student"
    )
    print("Created student user")

# Create ExtraInfo for student if it doesn't exist
try:
    student_extra = ExtraInfo.objects.get(id="2020001")
    print("Student ExtraInfo already exists")
except ExtraInfo.DoesNotExist:
    student_extra = ExtraInfo.objects.create(
        id="2020001",
        user=student_user,
        title="Mr.",
        sex="M",
        date_of_birth=datetime.date(2000, 1, 1),
        address="Test Address",
        phone_no=9876543210,
        user_type="student",
        department=cse_dept
    )
    print("Created student ExtraInfo")

# Create HoldsDesignation for student if it doesn't exist
try:
    student_holds = HoldsDesignation.objects.get(user=student_user, designation=student_desig)
    print("Student HoldsDesignation already exists")
except HoldsDesignation.DoesNotExist:
    student_holds = HoldsDesignation.objects.create(
        user=student_user,
        working=student_user,
        designation=student_desig
    )
    print("Created student HoldsDesignation")

# Create faculty user if it doesn't exist
try:
    faculty_user = User.objects.get(username="faculty")
    print("Faculty user already exists")
except User.DoesNotExist:
    faculty_user = User.objects.create_user(
        username="faculty",
        password="faculty123",
        email="faculty@example.com",
        first_name="Test",
        last_name="Faculty"
    )
    print("Created faculty user")

# Create faculty designation if it doesn't exist
try:
    faculty_desig = Designation.objects.get(name="faculty")
    print("Faculty designation already exists")
except Designation.DoesNotExist:
    faculty_desig = Designation.objects.create(
        name="faculty",
        full_name="Faculty",
        type="academic",
        category="faculty"
    )
    print("Created faculty designation")

# Create ExtraInfo for faculty if it doesn't exist
try:
    faculty_extra = ExtraInfo.objects.get(id="F001")
    print("Faculty ExtraInfo already exists")
except ExtraInfo.DoesNotExist:
    faculty_extra = ExtraInfo.objects.create(
        id="F001",
        user=faculty_user,
        title="Dr.",
        sex="M",
        date_of_birth=datetime.date(1980, 1, 1),
        address="Faculty Address",
        phone_no=9876543211,
        user_type="faculty",
        department=cse_dept
    )
    print("Created faculty ExtraInfo")

# Create HoldsDesignation for faculty if it doesn't exist
try:
    faculty_holds = HoldsDesignation.objects.get(user=faculty_user, designation=faculty_desig)
    print("Faculty HoldsDesignation already exists")
except HoldsDesignation.DoesNotExist:
    faculty_holds = HoldsDesignation.objects.create(
        user=faculty_user,
        working=faculty_user,
        designation=faculty_desig
    )
    print("Created faculty HoldsDesignation")

print("\nDummy users created successfully!")
print("\nLogin credentials:")
print("Admin: username=admin, password=admin123")
print("Student: username=student, password=student123")
print("Faculty: username=faculty, password=faculty123")