from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..selectors import get_active_visitors, get_incidents, get_recent_visits
from ..services import (
    RegistrationError,
    WorkflowError,
    deny_entry,
    issue_pass,
    log_incident,
    record_entry,
    record_exit,
    register_visitor,
    verify_visitor,
)
from .serializers import (
    DenialLogSerializer,
    DenyEntrySerializer,
    IssuePassSerializer,
    RecordMovementSerializer,
    RegisterVisitorSerializer,
    SecurityIncidentCreateSerializer,
    SecurityIncidentSerializer,
    VerifyVisitorSerializer,
    VisitSerializer,
    VisitorPassSerializer,
    VisitorSerializer,
)


class RegisterVisitorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterVisitorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            visitor, visit = register_visitor(serializer.validated_data)
        except RegistrationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

        try:
            visit = verify_visitor(serializer.validated_data, request.user)
        except WorkflowError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Verification successful.", "visit_status": visit.status})


class IssuePassView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IssuePassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            visit, visitor_pass, qr_data_uri = issue_pass(serializer.validated_data)
        except WorkflowError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "detail": "Pass issued",
            "visit_status": visit.status,
            "pass": VisitorPassSerializer(visitor_pass).data,
            "qr_code": qr_data_uri,
        })


class RecordEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecordMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            visit = record_entry(serializer.validated_data, request.user)
        except WorkflowError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Entry recorded", "visit_status": visit.status})


class RecordExitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecordMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            visit = record_exit(serializer.validated_data, request.user)
        except WorkflowError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Exit recorded", "visit_status": visit.status})


class DenyEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DenyEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        _visit, denial = deny_entry(serializer.validated_data)
        return Response({"detail": "Entry denied", "denial": DenialLogSerializer(denial).data})


class ActiveVisitorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active = get_active_visitors()
        return Response(VisitSerializer(active, many=True).data)


class RecentVisitsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 5))
        recent = get_recent_visits(limit=limit)
        return Response(VisitSerializer(recent, many=True).data)


class SecurityIncidentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get("limit", 20))
        incidents = get_incidents(limit=limit)
        return Response(SecurityIncidentSerializer(incidents, many=True).data)

    def post(self, request):
        serializer = SecurityIncidentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        incident = log_incident(serializer.validated_data, request.user)
        return Response(SecurityIncidentSerializer(incident).data, status=status.HTTP_201_CREATED)
