import base64
import io
import json

import pyqrcode
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    BlacklistEntry,
    DenialLog,
    EntryExitLog,
    SecurityIncident,
    VerificationLog,
    Visit,
    Visitor,
    VisitorPass,
    calculate_valid_until,
)
from .selectors import get_current_staff


class RegistrationError(Exception):
    pass


class WorkflowError(Exception):
    pass


def _generate_pass_qr(visitor_pass, visit):
    """Generate a PNG QR code as a base64 data-URI string."""
    qr_payload = json.dumps({
        "pass_number": visitor_pass.pass_number,
        "visit_id": visit.id,
        "visitor": visit.visitor.full_name,
        "id_number": visit.visitor.id_number,
        "host": visit.host_name,
        "department": visit.host_department,
        "zones": visitor_pass.authorized_zones,
        "valid_from": visitor_pass.valid_from.isoformat(),
        "valid_until": visitor_pass.valid_until.isoformat(),
        "vip": visitor_pass.is_vip_pass,
    })
    qr = pyqrcode.create(qr_payload, error="M")
    buffer = io.BytesIO()
    qr.png(buffer, scale=6, quiet_zone=2)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def register_visitor(data):
    """Register a visitor and create a new visit. Returns (visitor, visit).

    Raises RegistrationError if the visitor is blacklisted.
    """
    blacklist_hit = BlacklistEntry.objects.filter(
        id_number=data["id_number"], active=True,
    ).exists()
    if blacklist_hit:
        raise RegistrationError("Visitor is blacklisted; registration blocked.")

    visitor, _ = Visitor.objects.update_or_create(
        id_number=data["id_number"],
        defaults={
            "full_name": data["full_name"],
            "id_type": data["id_type"],
            "contact_phone": data["contact_phone"],
            "contact_email": data.get("contact_email", ""),
            "photo_reference": data.get("photo_reference", ""),
        },
    )

    visit = Visit.objects.create(
        visitor=visitor,
        purpose=data["purpose"],
        host_name=data["host_name"],
        host_department=data["host_department"],
        host_contact=data.get("host_contact", ""),
        expected_duration_minutes=data.get("expected_duration_minutes", 60),
        is_vip=data.get("is_vip", False),
    )
    return visitor, visit


def verify_visitor(data, user):
    """Verify a visitor's identity. Returns (visit, passed).

    Raises WorkflowError on verification failure.
    """
    visit = get_object_or_404(Visit, id=data["visit_id"])
    verifier = get_current_staff(user)

    VerificationLog.objects.create(
        visit=visit,
        verifier=verifier,
        method=data["method"],
        result=data["result"],
        notes=data.get("notes", ""),
    )

    if not data["result"]:
        visit.status = Visit.STATUS_DENIED
        visit.denial_reason = "verification_failed"
        visit.denial_remarks = data.get("notes", "")
        visit.save(update_fields=["status", "denial_reason", "denial_remarks"])
        DenialLog.objects.create(
            visit=visit,
            reason="verification_failed",
            remarks=data.get("notes", ""),
            escalated=True,
        )
        raise WorkflowError("Verification failed; entry denied.")

    visit.status = Visit.STATUS_VERIFIED
    visit.verified_at = timezone.now()
    visit.save(update_fields=["status", "verified_at"])
    return visit


def issue_pass(data):
    """Issue a visitor pass with QR code. Returns (visit, visitor_pass, qr_data_uri).

    Raises WorkflowError if the visit is in an invalid state.
    """
    visit = get_object_or_404(Visit, id=data["visit_id"])

    if visit.status in {Visit.STATUS_DENIED, Visit.STATUS_EXITED}:
        raise WorkflowError("Cannot issue pass for denied or closed visit.")
    if visit.status not in {Visit.STATUS_VERIFIED, Visit.STATUS_PASS_ISSUED}:
        raise WorkflowError("Visit must be verified before issuing a pass.")

    now = timezone.now()
    valid_until = calculate_valid_until(now, visit.expected_duration_minutes, visit.is_vip)
    visitor_pass, _ = VisitorPass.objects.update_or_create(
        visit=visit,
        defaults={
            "valid_from": now,
            "valid_until": valid_until,
            "authorized_zones": data.get("authorized_zones", "public"),
            "status": VisitorPass.PASS_ISSUED,
            "is_vip_pass": visit.is_vip,
        },
    )

    qr_data_uri = _generate_pass_qr(visitor_pass, visit)
    visitor_pass.barcode_data = qr_data_uri
    visitor_pass.save(update_fields=["barcode_data"])

    visit.status = Visit.STATUS_PASS_ISSUED
    visit.pass_issued_at = now
    visit.save(update_fields=["status", "pass_issued_at"])

    return visit, visitor_pass, qr_data_uri


def record_entry(data, user):
    """Record a visitor entry. Returns the visit.

    Raises WorkflowError if the visit is in an invalid state.
    """
    visit = get_object_or_404(Visit, id=data["visit_id"])
    if visit.status not in {Visit.STATUS_PASS_ISSUED, Visit.STATUS_INSIDE}:
        raise WorkflowError("Pass must be issued before entry.")

    EntryExitLog.objects.create(
        visit=visit,
        action=EntryExitLog.ACTION_ENTRY,
        gate_name=data["gate_name"],
        recorded_by=get_current_staff(user),
        items_declared=data.get("items_declared", ""),
    )

    visit.status = Visit.STATUS_INSIDE
    visit.entry_at = visit.entry_at or timezone.now()
    visit.save(update_fields=["status", "entry_at"])
    return visit


def record_exit(data, user):
    """Record a visitor exit. Returns the visit.

    Raises WorkflowError if the visitor is not inside.
    """
    visit = get_object_or_404(Visit, id=data["visit_id"])
    if visit.status != Visit.STATUS_INSIDE:
        raise WorkflowError("Visitor is not inside.")

    EntryExitLog.objects.create(
        visit=visit,
        action=EntryExitLog.ACTION_EXIT,
        gate_name=data["gate_name"],
        recorded_by=get_current_staff(user),
        items_declared=data.get("items_declared", ""),
    )

    visit.status = Visit.STATUS_EXITED
    visit.exit_at = timezone.now()
    visit.save(update_fields=["status", "exit_at"])

    visitor_pass = getattr(visit, "visitor_pass", None)
    if visitor_pass:
        visitor_pass.status = VisitorPass.PASS_RETURNED
        visitor_pass.save(update_fields=["status"])

    return visit


def deny_entry(data):
    """Deny entry for a visit. Returns (visit, denial_log)."""
    visit = get_object_or_404(Visit, id=data["visit_id"])
    visit.status = Visit.STATUS_DENIED
    visit.denial_reason = data["reason"]
    visit.denial_remarks = data.get("remarks", "")
    visit.save(update_fields=["status", "denial_reason", "denial_remarks"])

    denial = DenialLog.objects.create(
        visit=visit,
        reason=data["reason"],
        remarks=data.get("remarks", ""),
        escalated=data.get("escalated", False),
    )
    return visit, denial


def log_incident(data, user):
    """Log a security incident. Returns the incident."""
    visit = None
    visitor = None
    if data.get("visit_id"):
        visit = get_object_or_404(Visit, id=data["visit_id"])
        visitor = visit.visitor
    elif data.get("visitor_id"):
        visitor = get_object_or_404(Visitor, id=data["visitor_id"])

    return SecurityIncident.objects.create(
        visit=visit,
        visitor=visitor,
        recorded_by=get_current_staff(user),
        severity=data["severity"],
        issue_type=data["issue_type"],
        description=data["description"],
    )
