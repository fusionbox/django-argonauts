"""
Fusionbox widgets
"""
from django.forms import FileInput
from django.template import Context
from django.template.loader import get_template


class MultiFileWidget(FileInput):
    """
    Provides a widget to enable multifile uploads for a file field.

    Static Requirements:
        - jquery.js
        - jquery.multifile.js
    """
    multifile_template_name = "forms/fields/multifile.html"

    class Media:
        js = ("js/jquery.multifile.js", "js/jquery.multifile.preview.js")

    def __init__(self, *args, **kwargs):
        self.template_name = kwargs.pop("template_name",
                                        self.multifile_template_name)
        super(MultiFileWidget, self).__init__(*args, **kwargs)

    def container_id(self, name):
        """
        Given the name of the field, return the ID of the container that holds
        the files.
        """
        return "%s_attachment_container" % name

    def render(self, name, value, attrs=None):
        """
        Renders the multifile field template and returns the result as the
        rendered version of this field.
        """
        attrs.update({"multiple": ""})
        container_id = self.container_id(name)
        input_tag = super(FileInput, self).render(name, None, attrs=attrs)
        t = get_template(self.template_name)
        context = Context({
            "name": name,
            "input_tag": input_tag,
            "container_id": container_id,
        })
        return t.render(context)

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget"s name, returns the value
        of this widget. Returns None if it"s not provided.

        The change here from the default implementation from `FileInput` is
        that we are getting a list of files from the form.  Not just one.
        """
        try:
            return files.getlist(name)
        except AttributeError:
            return None
