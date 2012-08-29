Email
=========
Markdown-templated email.

An email template looks like this:

::

    ---
    subject: Hello, {{user.first_name}}
    ---
    Welcome to the site.

When using :func:`send_markdown_mail`, its output is placed in a layout to
produce a full html document::
::

    <!DOCTYPE html>
    <html>
        <body>
            {{content}}
        </body>
    </html>

The default layout is specified in ``settings.EMAIL_LAYOUT``, but can be
overridden on a per-email basis.

.. automodule:: fusionbox.mail
.. autofunction:: fusionbox.mail.create_markdown_mail
.. autofunction:: fusionbox.mail.send_markdown_mail
.. autofunction:: fusionbox.mail.render_template
.. autofunction:: fusionbox.mail.extract_frontmatter
