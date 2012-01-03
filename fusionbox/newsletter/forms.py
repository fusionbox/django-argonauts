from django import forms
from .models import Submission

class NewsletterSignupForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('email',)
