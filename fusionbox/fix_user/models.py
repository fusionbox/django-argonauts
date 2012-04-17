"""
This is a monkeypatch for the django user model to allow longer usernames up to 255 characters in length.

It patches:
    django.contrib.auth.models.User.username
    django.contrib.auth.forms: AuthenticationForm, UserCreationForm, UserChangeForm
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.core.validators import validate_email

User._meta.get_field('username').verbose_name = _('email')
User._meta.get_field('username').max_length = 255
User._meta.get_field('username').help_text = _("Required. 255 characters or fewer. Letters, numbers and @/./+/-/_ characters")
User._meta.get_field('username').validators[0].limit_value = 255

User._meta.get_field('email').max_length = 255
User._meta.get_field('email').validators[0].limit_value = 255

from django.contrib.auth.forms import AuthenticationForm

AuthenticationForm.base_fields['username'].max_length = 255  # I guess not needed
AuthenticationForm.base_fields['username'].widget.attrs['maxlength'] = 255  # html
AuthenticationForm.base_fields['username'].validators[0].limit_value = 255

from django.contrib.auth.forms import UserCreationForm

UserCreationForm.base_fields['username'].label = _('Email')
UserCreationForm.base_fields['username'].max_length = 255
UserCreationForm.base_fields['username'].widget.attrs['maxlength'] = 255  # html
UserCreationForm.base_fields['username'].validators[0].limit_value = 255
UserCreationForm.base_fields['username'].validators[1] = validate_email
UserCreationForm.base_fields['username'].error_messages['invalid'] = _(u'Enter a valid e-mail address.')
UserCreationForm.base_fields['username'].help_text = _("Required. 255 characters or fewer. Must be a valid email address")

from django.contrib.auth.forms import UserChangeForm

UserChangeForm.base_fields['username'].label = _('Email')
UserChangeForm.base_fields['username'].max_length = 255
UserChangeForm.base_fields['username'].widget.attrs['maxlength'] = 255  # html
UserChangeForm.base_fields['username'].validators[0].limit_value = 255
UserChangeForm.base_fields['username'].validators[1] = validate_email
UserChangeForm.base_fields['username'].error_messages['invalid'] = _(u'Enter a valid e-mail address.')
UserChangeForm.base_fields['username'].help_text = _("Required. 255 characters or fewer. Must be a valid email address")

old_init = UserChangeForm.__init__
def new_init(self, *args, **kwargs):
    ret = old_init(self, *args, **kwargs)
    self.fields['email'].label = 'Username'
    self.fields['email'].max_length = 255
    self.fields['email'].validators[0].limit_value = 255
    self.fields['email'].help_text = _("This will be set to the email")
    self.fields['email'].widget.attrs['maxlength'] = 254  # html
    self.fields['email'].widget.attrs['readonly'] = 'readonly'
    self.fields['email'].widget.attrs['disabled'] = 'disabled'
    return ret

UserChangeForm.__init__ = new_init


def copy_username_to_email(sender, instance, *args, **kwargs):
    """
    We remove the ``email`` field above, and this method "brings it back",
    by copying the username field to the email.
    """
    instance.email = instance.username

pre_save.connect(copy_username_to_email, User)
