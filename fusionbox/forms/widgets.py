"""
Fusionbox widgets
"""
from django.forms import FileInput
from django.utils.safestring import mark_safe


class MultiFileWidget(FileInput):
    """
    Provides a widget to enable multifile uploads for a file field.

    Static Requirements:
        - jquery.js
        - jquery.tmpl.js
        - jquery.multifile.js

    If you would like to use a different jquery-tmpl
    """

    class Media:
        js = ('js/jquery.tmpl.js', 'js/jquery.multifile.js',)

    def __init__(self, *args, **kwargs):
        self.render_jquery_tmpl_func = kwargs.pop('jquery_tmpl_func',
                self.render_jquery_tmpl)
        super(MultiFileWidget, self).__init__(*args, **kwargs)

    def render_jquery_tmpl(self, attrs):
        """
        Calculates the template string to use for the jQuery template.

        This determines the template to be used for each uploaded file.
        Two variables will be available in the template:
            - name (of uploaded file)
            - size (in bytes)
        """
        # TODO make this into a template.
        return u"""function(file){
return '<p class="uploaded_image">\
<a href="" class="remove_input">x</a> <span class="filename">\
 ' + file.name + '</span> <span class="filesize">[' + file.size + ' bytes]</span>\
<span class="preview"><img class="preview"></span>\
</p>';}"""

    def tmpl_id(self, name):
        """
        Given the name of the field, return the ID for the jquery template.
        """
        return "%s_uploaded_file" % name

    def container_id(self, name):
        """
        Given the name of the field, return the ID of the container that holds
        the files.
        """
        return "%s_attachment_container" % name

    def render(self, name, value, attrs=None):
        attrs.update({"multiple": ""})
        container_id = self.container_id(name)
        input_tag = super(FileInput, self).render(name, None, attrs=attrs)
        container = u'<div id="%s"></div>' % container_id
        binding = u"""
<script type="text/javascript">
  $('input[name={name}]').multifile('#{container_id}', {tmpl_func}, true);
</script>""".format(name=name, tmpl_func=self.render_jquery_tmpl(attrs),
                    container_id=container_id)

        return mark_safe(u"{input}{container}{binding}"\
                .format(
                    input=input_tag,
                    container=container,
                    binding=binding
                    )
                )

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.

        The change here from the default implementation from `FileInput` is
        that we are getting a list of files from the form.  Not just one.
        """
        try:
            return files.getlist(name)
        except AttributeError:
            return None
