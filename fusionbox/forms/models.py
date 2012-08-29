from django import forms
from django.middleware.csrf import get_token

import hashlib


class UncaptchaBase(object):
    def __init__(self, request, *args, **kwargs):
        super(UncaptchaBase, self).__init__(*args, **kwargs)
        hasher = hashlib.sha256()
        hasher.update(get_token(request))
        self.uncaptcha_value = hasher.hexdigest()

    def clean_uncaptcha(self):
        value = self.cleaned_data['uncaptcha']
        if not value == self.uncaptcha_value:
            raise forms.ValidationError("Incorrect uncaptcha value")
        return value


class UncaptchaForm(UncaptchaBase, forms.Form):
    uncaptcha = forms.CharField(required = False)


class UncaptchaModelForm(UncaptchaBase, forms.ModelForm):
    uncaptcha = forms.CharField(required = False)
