Contact
=======

Intro
------
The contact module is designed to be a DRY style contact form.

Installation
------------

-  Add ``'fusionbox.contact'`` to your ``INSTALLED_APPS``
-  Run `./manage.py syncdb` to create the necessary database tables
-  Create the required templates (see templates and views below)
-  Add urls to your url conf

Settings
--------

The contact module has the following settings values which which may be used to customize its behavior

``SITE_NAME``
  Name displayed on the success page for succesfult contact form submissions.  Defaults to 'Us'.

``CONTACT_FORM_RECIPIENTS``
  Iterable of email addresses.  Each person in this list will be emailed for each contact form recipient.  If not present, the contact module will use the values present in the Recipients table.  (See the Recipients section)

Views
-----

The contact module provides the following views located in ``fusionbox.contact.views``

**index(request[, template, email_template, contact_form, extra_context])**
  Renders the contact form

  URL name: ``contact_index``

  Optional arguments:
  
  *  ``template``: The path to the template to display the contact form.  Defaults to ``contact/index.html``
  *  ``email_template``: The markdown template used to send contact form submissions.  Defaults to ``mail/contact_form_submission.md``
  *  ``contact_form``: A form.  Defaults to ``fusionbox.contact.forms.ContactForm``
  *  ``extra_context``: A dictionary of extra context used for the response context

  All of these arguments may be passed in through your url conf::

        (r'^contact-us/index/$', 'fusionbox.contact.views.index', {'template': 'contact/index.html'}),

**success(request[, template, extra_context])**
  Renders the contact form

  URL name: ``contact_index``

  Optional arguments:
  
  *  ``template``: The path to the template to display the success page for successful contact form submissions.  Defaults to ``myapp/success.html``
  *  ``extra_context``: A dictionary of extra context used for the response context

  Similarly, these arguments can be passed in through your url conf::

        (r'^contact-us/success/$', 'fusionbox.contact.views.success', {'template': 'myapp/success.html'}),


URLS
----
You may include the urls for the contact module one of two ways.

1. Include the built in url conf somewhere in your site url conf::
  
    url(r'^contact-us/', include('fusionbox.contact.urls')),

2. Manually include the urls for both the ``index`` and ``success`` views.  Often this is the best way to customize the contact form or add extra context variables::
   
       (r'^contact-us/index/$', 'fusionbox.contact.views.index', {'template': 'myapp/index.html'}),
       (r'^contact-us/success/$', 'fusionbox.contact.views.success', {'template': 'myapp/success.html'}),

   

Templates
---------
The contact module requires three templates.

Primary Contact Form Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Default Location: ``contact/index.html``

This template is passed the context variable ``form``.

Example::

        <form method-"post" action-"{% url fusionbox.contact.views.index %}">
                {% csrf_token %}
                {{ form.non_field_errors }}
                <label for-"name">Name:</label>
                <p>{{ form.name.errors }}{{ form.name }}</p>
                <label for-"email">Email:</label>
                <p>{{ form.email.errors }}{{ form.email }}</p>
                <label for-"comments">Comments:</label>
                <p>{{ form.comment.errors }}{{ form.comment }}</p>
                <p><input type-"submit" name-"" id-"" value-"SUBMIT" class-"fr"/></p>
        </form>

Success Page Template
^^^^^^^^^^^^^^^^^^^^^
Default Location: ``contact/success.html``

Upon a successful contact form submission, the user is redirected to the success page.  The success template receives a context variable ``site_name`` which is populated from the settings file.  If this value is not present, this variable will default to 'Us'.

Example::

        <p>Thank you for contacting {{ site_name }}.  Someone will be in touch with you shortly!</p>

Email Template
^^^^^^^^^^^^^^
Default Location: ``mail/contact_form_submission.html``

Successful contact form submissions will be emailed using the fusionbox ``send_markdown_email`` function to a list of recipients.  The contact module will first look for ``CONTACT_FORM_RECIPIENTS`` in the settings file, and if not will use the values from the Recipients table.

Example::

        <p>Thank you for contacting {{ site_name }}.  Someone will be in touch with you shortly!</p>

Recipients
----------
The contact module has two methods for designating recipients to be emailed with the details from contact form submissions.  If the ``CONTACT_FORM_RECIPIENTS`` value is present in the settings file, those recipeints will be used.

If the setting is not present, the Recipients model will be registered for the admin site, and the values there will be used.
