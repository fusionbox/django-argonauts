from django import forms

from fusionbox.forms.models import UncaptchaModelForm

from fusionbox.contact.models import Submission

class ContactForm(UncaptchaModelForm):
    class Meta:
        model = Submission
        exclude = ('created_at',)
