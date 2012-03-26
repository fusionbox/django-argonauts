from django.contrib.auth.backends import ModelBackend
from django.conf import settings


def fancy_import(name):
    """
    This takes a fully qualified object name, like 'accounts.models.ProxyUser'
    and turns it into the accounts.models.ProxyUser object.
    """
    import_path, import_me = name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)

if getattr(settings, 'CUSTOM_USER_MODEL', False):
    User = fancy_import(settings.CUSTOM_USER_MODEL)
else:
    from django.contrib.auth.models import User


class CustomModelBackend(ModelBackend):
    """
    Extends the built in django auth backend to allow for a custom user object.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
