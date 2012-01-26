"""
Views for use with the fusionbox newsletter app.
"""
from django.shortcuts import render
from .forms import NewsletterSignupForm

def signup(request, form_template='newsletter/signup_form.html',
        success_template='newsletter/success.html', template = None):
    """
    This view takes care of accepting newsletter POST data from the user.

    It accepts 3 templates as keyword arguments:
        * `form_template`: name of the django template that contains the
        rendered form.
        * `success_template`: django template to render when a newsletter
        has been successfully submitted.
        * `template`: If set, this template will be used in place of both
        the `form_template` and `success_template`

    The name of the context variable to be returned to the template is
    `newsletter_signup_form`
    """
    form = NewsletterSignupForm(request.POST or None)
    if form.is_valid():
        form.save()
        template = success_template
    context = {
            'newsletter_signup_form': form
            }
    return render(request, template or form_template, context)
