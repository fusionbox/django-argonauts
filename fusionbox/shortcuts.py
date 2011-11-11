from django.core.exceptions import PermissionDenied

def get_permission_or_403(callable, user):
    if not callable(user):
        raise PermissionDenied
