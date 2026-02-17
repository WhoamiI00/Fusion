import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")

import django  # noqa: E402

django.setup()  # noqa: E402

from django.contrib.auth.models import User  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402

from applications.globals.models import DepartmentInfo, ExtraInfo  # noqa: E402
from applications.vms.models import BlacklistEntry  # noqa: E402


def print_response(label, response):
    try:
        payload = response.json()
    except ValueError:
        payload = response.content.decode("utf-8", errors="ignore")
    output = {
        "label": label,
        "status_code": response.status_code,
        "payload": payload,
    }
    print(json.dumps(output, indent=2, default=str))


client = APIClient()

dept, _ = DepartmentInfo.objects.get_or_create(name="Security")
user, _ = User.objects.get_or_create(username="vms_tester", defaults={"email": "vms_tester@example.com"})
ExtraInfo.objects.update_or_create(
    user=user,
    defaults={
        "id": "vms_tester",
        "title": "Mr.",
        "sex": "M",
        "user_status": "PRESENT",
        "address": "Main Gate",
        "phone_no": 9999990001,
        "user_type": "staff",
        "department": dept,
    },
)

client.force_authenticate(user=user)

# 1) Register visitor
register_payload = {
    "full_name": "Alice Visitor",
    "id_number": "ID12345",
    "id_type": "passport",
    "contact_phone": "9998887777",
    "contact_email": "alice@example.com",
    "photo_reference": "demo-photo-ref",
    "purpose": "Client meeting",
    "host_name": "Dr. Rao",
    "host_department": "CSE",
    "host_contact": "9990001111",
    "expected_duration_minutes": 60,
    "is_vip": False,
}
response = client.post("/vms/register/", register_payload, format="json")
print_response("register", response)

visit_id = None
if response.status_code == 201:
    visit_id = response.json().get("visit_id")

# 2) Verify visitor
if visit_id:
    verify_payload = {
        "visit_id": visit_id,
        "method": "manual",
        "result": True,
        "notes": "ID matched",
    }
    response = client.post("/vms/verify/", verify_payload, format="json")
    print_response("verify", response)

# 3) Issue pass
if visit_id:
    issue_payload = {"visit_id": visit_id, "authorized_zones": "lobby"}
    response = client.post("/vms/pass/", issue_payload, format="json")
    print_response("issue_pass", response)

# 4) Record entry
if visit_id:
    entry_payload = {"visit_id": visit_id, "gate_name": "Main Gate", "items_declared": "Laptop"}
    response = client.post("/vms/entry/", entry_payload, format="json")
    print_response("record_entry", response)

# 5) Active visitors
response = client.get("/vms/active/")
print_response("active_visitors", response)

# 6) Record exit
if visit_id:
    exit_payload = {"visit_id": visit_id, "gate_name": "Main Gate"}
    response = client.post("/vms/exit/", exit_payload, format="json")
    print_response("record_exit", response)

# 7) Log incident
if visit_id:
    incident_payload = {
        "visit_id": visit_id,
        "severity": "medium",
        "issue_type": "policy_violation",
        "description": "Entered restricted corridor",
    }
    response = client.post("/vms/incidents/", incident_payload, format="json")
    print_response("incident", response)

# 8) Deny entry (new visit)
second_payload = dict(register_payload)
second_payload.update({"id_number": "ID12346", "full_name": "Bob Visitor"})
response = client.post("/vms/register/", second_payload, format="json")
print_response("register_for_denial", response)

second_visit_id = None
if response.status_code == 201:
    second_visit_id = response.json().get("visit_id")

if second_visit_id:
    deny_payload = {
        "visit_id": second_visit_id,
        "reason": "invalid_id",
        "remarks": "Photo mismatch",
        "escalated": True,
    }
    response = client.post("/vms/deny/", deny_payload, format="json")
    print_response("deny_entry", response)

# 9) Blacklist check (expect 400)
BlacklistEntry.objects.update_or_create(id_number="BLK123", defaults={"reason": "Policy violation", "active": True})
blacklist_payload = dict(register_payload)
blacklist_payload.update({"id_number": "BLK123", "full_name": "Blocked Visitor"})
response = client.post("/vms/register/", blacklist_payload, format="json")
print_response("register_blacklisted", response)
