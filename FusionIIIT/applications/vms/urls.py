from django.urls import path

from .views import (
    ActiveVisitorsView,
    DenyEntryView,
    IssuePassView,
    RecordEntryView,
    RecordExitView,
    RegisterVisitorView,
    SecurityIncidentView,
    VerifyVisitorView,
)

app_name = "vms"

urlpatterns = [
    path("register/", RegisterVisitorView.as_view(), name="register"),
    path("verify/", VerifyVisitorView.as_view(), name="verify"),
    path("pass/", IssuePassView.as_view(), name="issue-pass"),
    path("entry/", RecordEntryView.as_view(), name="record-entry"),
    path("exit/", RecordExitView.as_view(), name="record-exit"),
    path("deny/", DenyEntryView.as_view(), name="deny-entry"),
    path("active/", ActiveVisitorsView.as_view(), name="active"),
    path("incidents/", SecurityIncidentView.as_view(), name="incidents"),
]
