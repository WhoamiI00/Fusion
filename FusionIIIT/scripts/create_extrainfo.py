import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")

import django
django.setup()

from django.contrib.auth.models import User
from applications.globals.models import DepartmentInfo, ExtraInfo

username = "ankitraj"
department_name = "cse"

try:
    dept, _ = DepartmentInfo.objects.get_or_create(name=department_name)
    user = User.objects.get(username=username)

    extra_info, created = ExtraInfo.objects.update_or_create(
        user=user,
        defaults={
            "id": user.username,
            "title": "Mr.",
            "sex": "M",
            "user_status": "PRESENT",
            "address": "Main Gate",
            "phone_no": 9999990001,
            "user_type": "staff",
            "department": dept,
        },
    )

    action = "Created" if created else "Updated"
    print(f"{action} ExtraInfo for user '{user.username}' in department '{dept.name}'.")
except User.DoesNotExist:
    print(f"Error: User '{username}' does not exist. Please create the user first.")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
