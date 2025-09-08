# This script fixes the issue with django-notifications-hq package
# The error is related to 'index_together' attribute in Meta class

def apply_patch():
    try:
        from notifications.base.models import AbstractNotification
        
        # Remove the index_together attribute from Meta class
        if hasattr(AbstractNotification._meta, 'index_together'):
            AbstractNotification._meta.index_together = []
            print("Successfully patched notifications package by removing index_together")
        else:
            print("No index_together attribute found in AbstractNotification._meta")
    except ImportError as e:
        print(f"Error importing notifications package: {e}")
    except Exception as e:
        print(f"Error applying patch: {e}")