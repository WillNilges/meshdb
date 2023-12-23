from django.db import models
from django.contrib.postgres.fields import ArrayField

from django.contrib.auth.models import Group
from django.db.models.fields import EmailField

NETWORK_NUMBER_MIN = 101
NETWORK_NUMBER_MAX = 8192


class Installer(Group):
    description = models.TextField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    class BuildingStatus(models.IntegerChoices):
        INACTIVE = 0
        ACTIVE = 1

    bin = models.IntegerField()
    building_status = models.IntegerField(choices=BuildingStatus.choices)
    street_address = models.TextField()
    city = models.TextField()
    state = models.TextField()
    zip_code = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    primary_nn = models.IntegerField(blank=True, null=True)
    node_name = models.TextField(default=None, blank=True, null=True)
    install_date = models.DateField(default=None, blank=True, null=True)
    abandon_date = models.DateField(default=None, blank=True, null=True)


class Member(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    email_address = models.EmailField()
    secondary_emails = ArrayField(EmailField(), null=True)
    phone_number = models.TextField(default=None, blank=True, null=True)
    slack_handle = models.TextField(default=None, blank=True, null=True)


class Install(models.Model):
    class InstallStatus(models.IntegerChoices):
        OPEN = 0
        SCHEDULED = 1
        BLOCKED = 2
        ACTIVE = 3
        INACTIVE = 4
        CLOSED = 5

    # Install Number (generated when form is submitted)
    install_number = models.IntegerField(primary_key=True)

    # The NN this install is associated with.
    # Through this, a building can have multiple NNs
    network_number = models.IntegerField(blank=True, null=True)

    # Summary status of install
    install_status = models.IntegerField(choices=InstallStatus.choices)

    # OSTicket ID
    ticket_id = models.IntegerField(blank=True, null=True)

    # Important dates
    request_date = models.DateField(default=None, blank=True, null=True)
    install_date = models.DateField(default=None, blank=True, null=True)
    abandon_date = models.DateField(default=None, blank=True, null=True)

    # Relation to Building
    building_id = models.ForeignKey(Building, on_delete=models.PROTECT)
    unit = models.TextField(default=None, blank=True, null=True)
    roof_access = models.BooleanField(default=False)

    # Relation to Member
    member_id = models.ForeignKey(Member, on_delete=models.PROTECT)
    notes = models.TextField(default=None, blank=True, null=True)
