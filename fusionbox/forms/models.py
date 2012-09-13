from django import forms
from fusionbox.forms.fields import UncaptchaField


class UncaptchaBase(object):
    """
    Base class for Uncaptcha forms to centralize the uncaptcha validation.
    """
    def clean_uncaptcha(self):
        value = self.cleaned_data['uncaptcha']
        if value is not None and not value == self.data.get('csrfmiddlewaretoken'):
            raise forms.ValidationError("Incorrect uncaptcha value")
        return value


class UncaptchaForm(UncaptchaBase, forms.Form):
    """
    Extension of ``django.forms.Form`` which adds an UncaptchaField to the
    form.
    """
    uncaptcha = UncaptchaField(required=False)


class UncaptchaModelForm(UncaptchaBase, forms.ModelForm):
    """
    Extension of ``django.forms.ModelForm`` which adds an UncaptchaField to the
    form.
    """
    uncaptcha = UncaptchaField(required=False)
