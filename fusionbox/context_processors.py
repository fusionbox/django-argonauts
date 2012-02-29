from django.conf import settings as global_settings

def settings(request):
    """
    Populates template env with all settings included in SETTINGS_TO_INCLUDE.
    """
    ret = {}

    for i in global_settings.SETTINGS_TO_INCLUDE:
        ret[i] = getattr(global_settings, i)
    return ret
