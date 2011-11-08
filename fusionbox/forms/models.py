from django import forms

import hashlib

class UncaptchaBase(object):
    uncaptcha = forms.CharField(required = False)

    def __init__(self, request, *args, **kwargs):
        super(UncaptchaBase, self).__init__(*args, **kwargs)
        hasher = hashlib.sha256()
        hasher.update(request.session.session_key)
        self.uncaptcha_value = hasher.hexdigest()

    def clean_uncaptcha(self):
        value = self.cleaned_data['uncaptcha']
        if not value = self.uncaptcha_value:
            raise forms.ValidationError("Incorrect uncaptcha value")
        return value

class UncaptchaForm(UncaptchaBase, forms.Form):
    pass

class UncaptchaModelForm(UncaptchaBase, forms.ModelForm):
    pass
