from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = 'notification'
    
    def ready(self):
        # Import and apply the monkey patch to fix the notifications package
        from .monkey_patch import apply_patch
        apply_patch()

