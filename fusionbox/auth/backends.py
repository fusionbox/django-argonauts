from django.contrib.auth.backends import ModelBackend
from django.conf import settings

def fancy_import(name):
    """
    This takes a fully qualified object name, like 'accounts.models.ProxyUser'
    and turns it into the accounts.models.ProxyUser object.
    """

    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

if getattr(settings, 'CUSTOM_USER_MODLE', False):
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
