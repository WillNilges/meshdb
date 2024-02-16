import json

from django.contrib.auth.models import User
from django.test import Client, TestCase

from ..models import Building, Sector


class TestSector(TestCase):
    c = Client()

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="admin_password", email="admin@example.com"
        )
        self.c.login(username="admin", password="admin_password")

        self.building_1 = Building(
            building_status=Building.BuildingStatus.ACTIVE,
            address_truth_sources="",
            latitude=0,
            longitude=0,
            altitude=0,
            invalid=True,
        )
        self.building_1.save()

    def test_new_sector(self):
        response = self.c.post(
            "/api/v1/sectors/",
            {
                "name": "Vernon",
                "device_name": "LAP-120",
                "building": self.building_1.id,
                "status": "Active",
                "azimuth": 0,
                "width": 120,
                "radius": 0.3,
            },
        )
        code = 201
        self.assertEqual(
            code,
            response.status_code,
            f"status code incorrect. Should be {code}, but got {response.status_code}",
        )

    def test_broken_link(self):
        response = self.c.post(
            "/api/v1/sectors/",
            {
                "name": "Vernon",
                "device_name": "",
                "building": "",
                "status": "",
                "azimuth": 0,
                "width": 120,
                "radius": 0.3,
            },
        )
        code = 400
        self.assertEqual(
            code,
            response.status_code,
            f"status code incorrect. Should be {code}, but got {response.status_code}",
        )

    def test_recursive_get(self):
        sector = Sector(
            name="Vernon",
            device_name="LAP-120",
            building=self.building_1,
            status="Active",
            azimuth=0,
            width=120,
            radius=0.3,
        )
        sector.save()

        response = self.c.get(f"/api/v1/sectors/{sector.id}/")

        code = 200
        self.assertEqual(
            code,
            response.status_code,
            f"status code incorrect. Should be {code}, but got {response.status_code}",
        )

        response_obj = json.loads(response.content)
        self.assertEqual(response_obj["status"], "Active")
        self.assertEqual(
            response_obj["building"],
            {
                "address_truth_sources": "",
                "altitude": 0.0,
                "bin": None,
                "building_status": "Active",
                "city": None,
                "id": 76,
                "installs": [],
                "invalid": True,
                "latitude": 0.0,
                "links_from": [],
                "links_to": [],
                "longitude": 0.0,
                "node_name": None,
                "notes": None,
                "primary_nn": None,
                "state": None,
                "street_address": None,
                "zip_code": None,
            },
        )
