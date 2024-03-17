from datetime import datetime

from django.db.models import Count, F, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions

from meshapi.models import Building, Device, Install, Link, Node, Sector
from meshapi.serializers import (
    ALLOWED_INSTALL_STATUSES,
    EXCLUDED_INSTALL_STATUSES,
    MapDataInstallSerializer,
    MapDataLinkSerializer,
    MapDataSectorSerializer,
)


@extend_schema_view(
    get=extend_schema(
        tags=["Website Map Data"],
        auth=[],
        summary='Complete list of all "Nodes" (mostly Installs with some fake installs generated to solve NN re-use), '
        "unpaginated, in the format expected by the website map. (Warning: This endpoint is a legacy format and may be "
        "deprecated/removed in the future)",
    ),
)
class MapDataNodeList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataInstallSerializer
    pagination_class = None

    def get_queryset(self):
        all_installs = []

        queryset = (
            Install.objects.select_related("building")
            .select_related("node")
            .filter(~Q(status__in=EXCLUDED_INSTALL_STATUSES))
        )

        for install in queryset:
            all_installs.append(install)

        # We need to make sure there is an entry on the map for every NN, and since we excluded the
        # NN assigned rows in the query above, we need to go through the Node objects and
        # include the nns we haven't already covered via install num
        covered_nns = {
            install.install_number
            for install in all_installs
            if install.node and install.install_number == install.node.network_number
        }
        for node in Node.objects.filter(
            ~Q(status=Node.NodeStatus.INACTIVE) & Q(installs__status__in=ALLOWED_INSTALL_STATUSES)
        ):
            if node.network_number not in covered_nns:
                # Arbitrarily pick a representative install for the details of the "Fake" node,
                # preferring active installs if possible
                representative_install = node.installs.filter(status=Install.InstallStatus.ACTIVE).first()
                if not representative_install:
                    representative_install = node.installs.first()

                all_installs.append(
                    Install(
                        install_number=node.network_number,
                        status=Install.InstallStatus.NN_REASSIGNED,
                        building=representative_install.building,
                        request_date=representative_install.request_date,
                        roof_access=representative_install.roof_access,
                    ),
                )
                covered_nns.add(node.network_number)

        all_installs.sort(key=lambda i: i.install_number)
        return all_installs

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)

        access_points = []
        for device in Device.objects.filter(
            Q(status=Device.DeviceStatus.ACTIVE)
            & (~Q(node__latitude=F("latitude")) | ~Q(node__longitude=F("longitude")))
        ):
            install_date = (
                int(
                    datetime.combine(
                        device.install_date,
                        datetime.min.time(),
                    ).timestamp()
                    * 1000
                )
                if device.install_date
                else None
            )
            ap = {
                "id": 1_000_000 + device.id,  # Hacky but we have no choice
                "name": device.name,
                "status": "Installed",
                "coordinates": [device.longitude, device.latitude, None],
                "roofAccess": False,
                "notes": "AP",
                "panoramas": [],
            }

            if install_date:
                ap["requestDate"] = install_date
                ap["installDate"] = install_date

            access_points.append(ap)

        response.data.extend(access_points)

        return response


@extend_schema_view(
    get=extend_schema(
        tags=["Website Map Data"],
        auth=[],
        summary="Complete list of all Links, unpaginated, in the format expected by the website map. "
        "(Warning: This endpoint is a legacy format and may be deprecated/removed in the future)",
    ),
)
class MapDataLinkList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataLinkSerializer
    pagination_class = None
    queryset = (
        Link.objects.prefetch_related("from_device__node__installs")
        .prefetch_related("to_device__node__installs")
        .exclude(status__in=[Link.LinkStatus.INACTIVE])
        .exclude(to_device__node__status=Node.NodeStatus.INACTIVE)
        .exclude(from_device__node__status=Node.NodeStatus.INACTIVE)
        # TODO: Possibly re-enable the below filters? They make make the map arguably more accurate,
        #  but less consistent with the current one by removing links between devices that are
        #  inactive in UISP
        # .exclude(from_device__status=Device.DeviceStatus.INACTIVE)
        # .exclude(to_device__status=Device.DeviceStatus.INACTIVE)
    )

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)

        # Slightly hacky way to show ethernet cable runs on the old map.
        # We just look for nodes where there are installs on separate buildings
        # and add fake link objects to connect the installs on those other buildings to
        # the node dot
        cable_runs = []
        for node in (
            Node.objects.prefetch_related("buildings__installs")
            .annotate(num_buildings=Count("buildings"))
            .filter(num_buildings__gt=1)
        ):
            for building in node.buildings.all():
                active_installs = building.installs.filter(status=Install.InstallStatus.ACTIVE).order_by(
                    "install_number"
                )
                if active_installs:
                    from_install = active_installs.first().install_number
                    if from_install != node.network_number:
                        cable_runs.append(
                            {
                                "from": from_install,
                                "to": node.network_number,
                                "status": "active",
                            }
                        )

        response.data.extend(cable_runs)

        return response


@extend_schema_view(
    get=extend_schema(
        tags=["Website Map Data"],
        auth=[],
        summary="Complete list of all Sectors, unpaginated, in the format expected by the website map. "
        "(Warning: This endpoint is a legacy format and may be deprecated/removed in the future)",
    ),
)
class MapDataSectorList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MapDataSectorSerializer
    pagination_class = None
    queryset = Sector.objects.prefetch_related("node__installs").filter(~Q(status__in=[Device.DeviceStatus.INACTIVE]))
