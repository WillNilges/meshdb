import json
import os

from django.forms import widgets
from django.template import loader
from django.utils.safestring import mark_safe
from django_jsonform.widgets import JSONFormWidget


class PanoramaViewer(JSONFormWidget):
    pano_template_name = "widgets/panorama_viewer.html"

    def __init__(self, schema):
        super().__init__(schema)

    def pano_get_context(self, name, value, attrs=None):
        value_as_array = json.loads(value)
        return {
            "widget": {
                "name": name,
                "value": value_as_array,
            }
        }

    def render(self, name, value, attrs=None, renderer=None):
        if "DISALLOW_PANO_EDITS" in os.environ:
            super_template = ""
        else:
            # Render the JSONFormWidget to allow editing of the panoramas
            super_template = super().render(name, value, attrs, renderer)

        # Then, render the panoramas for viewing
        context = self.pano_get_context(name, value, attrs)
        pano_template = loader.get_template(self.pano_template_name).render(context)

        template = super_template + pano_template
        return mark_safe(template)


class DeviceIPAddressWidget(widgets.TextInput):
    template_name = "widgets/ip_address.html"
