"""
This is a monkeypatch for the django user model to allow longer usernames up to 255 characters in length.

It patches:
    django.contrib.auth.models.User.username
    django.contrib.auth.forms: AuthenticationForm, UserCreationForm, UserChangeForm
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

User._meta.get_field('username').verbose_name = _('email')
User._meta.get_field('username').max_length = 255
User._meta.get_field('username').help_text = _("Required. 255 characters or fewer. Letters, numbers and @/./+/-/_ characters")
User._meta.get_field('username').validators[0].limit_value = 255

User._meta.get_field('email').max_length = 255
User._meta.get_field('email').validators[0].limit_value = 255

from django.contrib.auth.forms import AuthenticationForm

AuthenticationForm.base_fields['username'].max_length = 255 # I guess not needed
AuthenticationForm.base_fields['username'].widget.attrs['maxlength'] = 255 # html
AuthenticationForm.base_fields['username'].validators[0].limit_value = 255

from django.contrib.auth.forms import UserCreationForm

UserCreationForm.base_fields['username'].label = 'Email'
UserCreationForm.base_fields['username'].max_length = 255
UserCreationForm.base_fields['username'].widget.attrs['maxlength'] = 255 # html
UserCreationForm.base_fields['username'].validators[0].limit_value = 255
UserCreationForm.base_fields['username'].help_text = _("Required. 255 characters or fewer. Letters, numbers and @/./+/-/_ characters")

from django.contrib.auth.forms import UserChangeForm

UserChangeForm.base_fields['username'].max_length = 255
UserChangeForm.base_fields['username'].widget.attrs['maxlength'] = 255 # html
UserChangeForm.base_fields['username'].validators[0].limit_value = 255
UserChangeForm.base_fields['username'].help_text = _("Required. 255 characters or fewer. Letters, numbers and @/./+/-/_ characters")

UserChangeForm.base_fields['email'].max_length = 255
UserChangeForm.base_fields['email'].widget.attrs['maxlength'] = 255 # html
UserChangeForm.base_fields['email'].validators[0].limit_value = 255
