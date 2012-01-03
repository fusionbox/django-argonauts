from django.shortcuts import render
from newsletter.forms import NewsletterSignupForm

def signup(request, form_template='newsletter/signup_form.html',
        success_template='newsletter/success.html', template = None):
    form = NewsletterSignupForm(request.POST or None)
    if form.is_valid():
        form.save()
        template = success_template
    context = {
            'newsletter_signup_form': form
            }
    return render(request, template or form_template, context)
