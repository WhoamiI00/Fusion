import base64
import io
import json

import pyqrcode
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.globals.models import ExtraInfo

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
from .serializers import (
    DenialLogSerializer,
    DenyEntrySerializer,
    RegisterVisitorSerializer,
    RecordMovementSerializer,
    SecurityIncidentCreateSerializer,
    SecurityIncidentSerializer,
    VerifyVisitorSerializer,
    VisitSerializer,
    VisitorPassSerializer,
    VisitorSerializer,
    IssuePassSerializer,
)


def _current_staff(request):
    return ExtraInfo.objects.filter(user=request.user).first()


class RegisterVisitorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterVisitorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        blacklist_hit = BlacklistEntry.objects.filter(id_number=data["id_number"], active=True).exists()
        if blacklist_hit:
            return Response({"detail": "Visitor is blacklisted; registration blocked."}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response(
            {
                "visit_id": visit.id,
                "visitor": VisitorSerializer(visitor).data,
                "status": visit.status,
                "registered_at": visit.registered_at,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyVisitorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyVisitorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        visit = get_object_or_404(Visit, id=data["visit_id"])
        verifier = _current_staff(request)

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
            return Response({"detail": "Verification failed; entry denied."}, status=status.HTTP_400_BAD_REQUEST)

        visit.status = Visit.STATUS_VERIFIED
        visit.verified_at = timezone.now()
        visit.save(update_fields=["status", "verified_at"])
        return Response({"detail": "Verification successful.", "visit_status": visit.status})


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


class IssuePassView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IssuePassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        visit = get_object_or_404(Visit, id=data["visit_id"])
        if visit.status in {Visit.STATUS_DENIED, Visit.STATUS_EXITED}:
            return Response({"detail": "Cannot issue pass for denied or closed visit."}, status=status.HTTP_400_BAD_REQUEST)
        if visit.status not in {Visit.STATUS_VERIFIED, Visit.STATUS_PASS_ISSUED}:
            return Response({"detail": "Visit must be verified before issuing a pass."}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response(
            {
                "detail": "Pass issued",
                "visit_status": visit.status,
                "pass": VisitorPassSerializer(visitor_pass).data,
                "qr_code": qr_data_uri,
            }
        )


class RecordEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecordMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        visit = get_object_or_404(Visit, id=data["visit_id"])
        if visit.status not in {Visit.STATUS_PASS_ISSUED, Visit.STATUS_INSIDE}:
            return Response({"detail": "Pass must be issued before entry."}, status=status.HTTP_400_BAD_REQUEST)

        EntryExitLog.objects.create(
            visit=visit,
            action=EntryExitLog.ACTION_ENTRY,
            gate_name=data["gate_name"],
            recorded_by=_current_staff(request),
            items_declared=data.get("items_declared", ""),
        )

        visit.status = Visit.STATUS_INSIDE
        visit.entry_at = visit.entry_at or timezone.now()
        visit.save(update_fields=["status", "entry_at"])

        return Response({"detail": "Entry recorded", "visit_status": visit.status})


class RecordExitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecordMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        visit = get_object_or_404(Visit, id=data["visit_id"])
        if visit.status != Visit.STATUS_INSIDE:
            return Response({"detail": "Visitor is not inside."}, status=status.HTTP_400_BAD_REQUEST)

        EntryExitLog.objects.create(
            visit=visit,
            action=EntryExitLog.ACTION_EXIT,
            gate_name=data["gate_name"],
            recorded_by=_current_staff(request),
            items_declared=data.get("items_declared", ""),
        )

        visit.status = Visit.STATUS_EXITED
        visit.exit_at = timezone.now()
        visit.save(update_fields=["status", "exit_at"])

        visitor_pass = getattr(visit, "visitor_pass", None)
        if visitor_pass:
            visitor_pass.status = VisitorPass.PASS_RETURNED
            visitor_pass.save(update_fields=["status"])

        return Response({"detail": "Exit recorded", "visit_status": visit.status})


class DenyEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DenyEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

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

        return Response({"detail": "Entry denied", "denial": DenialLogSerializer(denial).data})


class ActiveVisitorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active = Visit.objects.filter(status__in=[Visit.STATUS_INSIDE, Visit.STATUS_PASS_ISSUED]).order_by("-registered_at")
        return Response(VisitSerializer(active, many=True).data)


class RecentVisitsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 5))
        recent = Visit.objects.order_by("-registered_at")[:limit]
        return Response(VisitSerializer(recent, many=True).data)


class SecurityIncidentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 20))
        incidents = SecurityIncident.objects.order_by("-created_at")[:limit]
        return Response(SecurityIncidentSerializer(incidents, many=True).data)

    def post(self, request):
        serializer = SecurityIncidentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        visit = None
        visitor = None
        if data.get("visit_id"):
            visit = get_object_or_404(Visit, id=data["visit_id"])
            visitor = visit.visitor
        elif data.get("visitor_id"):
            visitor = get_object_or_404(Visitor, id=data["visitor_id"])

        incident = SecurityIncident.objects.create(
            visit=visit,
            visitor=visitor,
            recorded_by=_current_staff(request),
            severity=data["severity"],
            issue_type=data["issue_type"],
            description=data["description"],
        )

        return Response(SecurityIncidentSerializer(incident).data, status=status.HTTP_201_CREATED)
