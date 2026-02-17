from django.contrib import admin

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

admin.site.register(Visitor)
admin.site.register(BlacklistEntry)
admin.site.register(Visit)
admin.site.register(VisitorPass)
admin.site.register(VerificationLog)
admin.site.register(DenialLog)
admin.site.register(EntryExitLog)
admin.site.register(SecurityIncident)
