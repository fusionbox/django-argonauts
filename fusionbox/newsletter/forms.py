"""
Basic newsletter signup form.

"""
from django import forms
from .models import Submission

class NewsletterSignupForm(forms.ModelForm):
    """
    :class:`NewsletterSignupForm` is a simple :class:`ModelForm` that 
    requires a valid, unique email.
    """

    class Meta:
        model = Submission
        fields = ('email',)
