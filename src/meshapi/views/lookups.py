from rest_framework import filters, generics

from meshapi.models import Building, Install, Member
from meshapi.serializers import BuildingSerializer, InstallSerializer, MemberSerializer

# https://medium.com/geekculture/make-an-api-search-endpoint-with-django-rest-framework-111f307747b8


class LookupMember(generics.ListAPIView):
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = MemberSerializer

    def get_queryset(self):
        # TODO: Validate Parameters?

        query_dict = {k: v for k, v in self.request.query_params.items() if v}
        filter_keyword_arguments_dict = {}
        for k, v in query_dict.items():
            if k == "name":
                filter_keyword_arguments_dict["name__icontains"] = v
            if k == "email_address":
                filter_keyword_arguments_dict["primary_email_address__icontains"] = v
            if k == "phone_number":
                filter_keyword_arguments_dict["phone_number__icontains"] = v
        queryset = Member.objects.filter(**filter_keyword_arguments_dict)
        return queryset


class LookupInstall(generics.ListAPIView):
    # TODO: Add more search fields later
    search_fields = ["install_number", "network_number", "member", "building", "install_status"]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = InstallSerializer

    def get_queryset(self):
        # TODO: Validate Parameters?

        query_dict = {k: v for k, v in self.request.query_params.items() if v}
        filter_keyword_arguments_dict = {}
        for k, v in query_dict.items():
            if k in self.search_fields:
                filter_keyword_arguments_dict[f"{k}__exact"] = v
        queryset = Install.objects.filter(**filter_keyword_arguments_dict)
        return queryset


class LookupBuilding(generics.ListAPIView):
    search_fields = [
        "install",
        "bin",
        "building_status",
        "street_address",
        "city",
        "state",
        "zip_code",
        "primary_nn",
    ]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = BuildingSerializer

    def get_queryset(self):
        # TODO: Validate Parameters?

        query_dict = {k: v for k, v in self.request.query_params.items() if v}
        filter_keyword_arguments_dict = {}
        for k, v in query_dict.items():
            if k in self.search_fields:
                filter_keyword_arguments_dict[f"{k}__exact"] = v
        queryset = Building.objects.filter(**filter_keyword_arguments_dict)
        return queryset
