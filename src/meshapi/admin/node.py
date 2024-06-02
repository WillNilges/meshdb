from django.contrib import admin
from django.contrib.admin.options import forms
from import_export import resources
from import_export.admin import ExportActionMixin, ImportExportModelAdmin

from meshapi.admin.inlines import (
    BuildingMembershipInline,
    DeviceInline,
    InstallInline,
    NodeLinkInline,
    NonrelatedBuildingInline,
    PanoramaInline,
    SectorInline,
)
from meshapi.models import Node

admin.site.site_header = "MeshDB Admin"
admin.site.site_title = "MeshDB Admin Portal"
admin.site.index_title = "Welcome to MeshDB Admin Portal"


class NodeImportExportResource(resources.ModelResource):
    def before_import(self, dataset, **kwargs):
        if "network_number" not in dataset.headers:
            dataset.headers.append("network_number")
        super().before_import(dataset, **kwargs)

    class Meta:
        model = Node
        import_id_fields = ("network_number",)


class NodeAdminForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = "__all__"


@admin.register(Node)
class NodeAdmin(ImportExportModelAdmin, ExportActionMixin):
    form = NodeAdminForm
    resource_classes = [NodeImportExportResource]
    search_fields = [
        "network_number__iexact",
        "name__icontains",
        "buildings__street_address__icontains",
        "notes__icontains",
    ]
    list_filter = ["status", ("name", admin.EmptyFieldListFilter), "install_date", "abandon_date"]
    list_display = ["__network_number__", "name", "status", "address", "install_date"]
    fieldsets = [
        (
            "Details",
            {
                "fields": [
                    "status",
                    "type",
                    "name",
                ]
            },
        ),
        (
            "Location",
            {
                "fields": [
                    "latitude",
                    "longitude",
                    "altitude",
                ]
            },
        ),
        (
            "Dates",
            {
                "fields": [
                    "install_date",
                    "abandon_date",
                ]
            },
        ),
        (
            "Misc",
            {
                "fields": [
                    "notes",
                ]
            },
        ),
    ]
    inlines = [
        PanoramaInline,
        InstallInline,
        NonrelatedBuildingInline,
        BuildingMembershipInline,
        DeviceInline,
        SectorInline,
        NodeLinkInline,
    ]

    def address(self, obj):
        return obj.buildings.first()
