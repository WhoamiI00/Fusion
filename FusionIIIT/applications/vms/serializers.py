from rest_framework import serializers

from .models import (
    BlacklistEntry,
    DenialLog,
    EntryExitLog,
    SecurityIncident,
    VerificationLog,
    Visit,
    Visitor,
    VisitorPass,
)


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = "__all__"


class VisitSerializer(serializers.ModelSerializer):
    visitor = VisitorSerializer()
    gate_name = serializers.SerializerMethodField()
    authorized_zones = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = "__all__"

    def get_gate_name(self, obj):
        last_log = obj.movement_logs.order_by("-created_at").first()
        return last_log.gate_name if last_log else ""

    def get_authorized_zones(self, obj):
        try:
            return obj.visitor_pass.authorized_zones
        except VisitorPass.DoesNotExist:
            return ""


class VisitorPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorPass
        fields = "__all__"


class VerificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationLog
        fields = "__all__"


class DenialLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DenialLog
        fields = "__all__"


class EntryExitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryExitLog
        fields = "__all__"


class SecurityIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIncident
        fields = "__all__"


class RegisterVisitorSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    id_number = serializers.CharField()
    id_type = serializers.ChoiceField(choices=Visitor.ID_TYPES)
    contact_phone = serializers.CharField()
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    photo_reference = serializers.CharField(required=False, allow_blank=True)
    purpose = serializers.CharField()
    host_name = serializers.CharField()
    host_department = serializers.CharField()
    host_contact = serializers.CharField(required=False, allow_blank=True)
    expected_duration_minutes = serializers.IntegerField(min_value=5, default=60)
    is_vip = serializers.BooleanField(default=False)


class VerifyVisitorSerializer(serializers.Serializer):
    visit_id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=VerificationLog.METHODS, default=VerificationLog.METHOD_MANUAL)
    result = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True)


class IssuePassSerializer(serializers.Serializer):
    visit_id = serializers.IntegerField()
    authorized_zones = serializers.CharField(default="public")


class RecordMovementSerializer(serializers.Serializer):
    visit_id = serializers.IntegerField()
    gate_name = serializers.CharField()
    items_declared = serializers.CharField(required=False, allow_blank=True)


class DenyEntrySerializer(serializers.Serializer):
    visit_id = serializers.IntegerField()
    reason = serializers.CharField()
    remarks = serializers.CharField(required=False, allow_blank=True)
    escalated = serializers.BooleanField(default=False)


class SecurityIncidentCreateSerializer(serializers.Serializer):
    visit_id = serializers.IntegerField(required=False)
    visitor_id = serializers.IntegerField(required=False)
    severity = serializers.ChoiceField(choices=SecurityIncident.SEVERITIES)
    issue_type = serializers.ChoiceField(choices=SecurityIncident.ISSUE_TYPES)
    description = serializers.CharField()
