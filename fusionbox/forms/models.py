from django import forms
from fusionbox.forms.forms import UncaptchaBase
from fusionbox.forms.fields import UncaptchaField


class UncaptchaModelForm(UncaptchaBase, forms.ModelForm):
    """
    Extension of ``django.forms.ModelForm`` which adds an UncaptchaField to the
    form.
    """
    uncaptcha = UncaptchaField(required=False)
