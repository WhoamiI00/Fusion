from applications.globals.models import ExtraInfo

from .models import SecurityIncident, Visit


def get_current_staff(user):
    """Return the ExtraInfo record for the given user, or None."""
    return ExtraInfo.objects.filter(user=user).first()


def get_active_visitors():
    """Return visits that are currently inside or have a pass issued."""
    return Visit.objects.filter(
        status__in=[Visit.STATUS_INSIDE, Visit.STATUS_PASS_ISSUED],
    ).order_by("-registered_at")


def get_recent_visits(limit=5):
    """Return the most recent visits, ordered newest-first."""
    return Visit.objects.order_by("-registered_at")[:limit]


def get_incidents(limit=20):
    """Return the most recent security incidents."""
    return SecurityIncident.objects.order_by("-created_at")[:limit]
