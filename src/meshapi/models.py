from django.contrib.auth.models import Group, Permission
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.fields import EmailField

NETWORK_NUMBER_MIN = 101
NETWORK_NUMBER_MAX = 8192

#def create_groups():
#    models = ['building', 'member', 'install', 'link', 'sector',]
#    all_permissions = Permission.objects.all()
#    
#    admin, _ = Group.objects.get_or_create(name="Admin")
#    installer, _ = Group.objects.get_or_create(name="Installer")
#    
#    read_only, _ = Group.objects.get_or_create(name="Read Only")
#    for p in all_permissions:
#        code = p.codename
#        print(code)
#
#create_groups()


class Building(models.Model):
    class BuildingStatus(models.IntegerChoices):
        INACTIVE = 0
        ACTIVE = 1

    bin = models.IntegerField(blank=True, null=True)
    building_status = models.IntegerField(choices=BuildingStatus.choices)
    street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    invalid = models.BooleanField(default=False)
    address_truth_sources = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(blank=True, null=True)
    primary_nn = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(NETWORK_NUMBER_MIN),
            MaxValueValidator(NETWORK_NUMBER_MAX),
        ],
    )
    node_name = models.TextField(default=None, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        node_name_str = f"{self.node_name} | " if self.node_name is not None else ""
        return f"{node_name_str}{self.street_address}"


class Member(models.Model):
    name = models.TextField()
    email_address = models.EmailField(null=True)
    secondary_emails = ArrayField(EmailField(), null=True)
    phone_number = models.TextField(default=None, blank=True, null=True)
    slack_handle = models.TextField(default=None, blank=True, null=True)
    invalid = models.BooleanField(default=False)
    contact_notes = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return self.name


class Install(models.Model):
    class InstallStatus(models.IntegerChoices):
        OPEN = 0
        SCHEDULED = 1
        NN_ASSIGNED = 2
        BLOCKED = 3
        ACTIVE = 4
        INACTIVE = 5
        CLOSED = 6

    # Install Number (generated when form is submitted)
    install_number = models.AutoField(
        primary_key=True,
        db_column="install_number",
    )

    # The NN this install is associated with.
    # Through this, a building can have multiple NNs
    network_number = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(NETWORK_NUMBER_MIN), MaxValueValidator(NETWORK_NUMBER_MAX)],
    )

    # Summary status of install
    install_status = models.IntegerField(choices=InstallStatus.choices)

    # OSTicket ID
    ticket_id = models.IntegerField(blank=True, null=True)

    # Important dates
    request_date = models.DateField()
    install_date = models.DateField(default=None, blank=True, null=True)
    abandon_date = models.DateField(default=None, blank=True, null=True)

    # Relation to Building
    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    unit = models.TextField(default=None, blank=True, null=True)
    roof_access = models.BooleanField(default=False)

    # Relation to Member
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    referral = models.TextField(default=None, blank=True, null=True)
    notes = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return f"Install #{str(self.install_number)}"


class Link(models.Model):
    class LinkStatus(models.TextChoices):
        DEAD = "Dead"
        PLANNED = "Planned"
        ACTIVE = "Active"

    class LinkType(models.TextChoices):
        STANDARD = "Standard"
        VPN = "VPN"
        MMWAVE = "MMWave"
        FIBER = "Fiber"

    from_building = models.ForeignKey(Building, on_delete=models.PROTECT, related_name="link_from")
    to_building = models.ForeignKey(Building, on_delete=models.PROTECT, related_name="link_to")

    status = models.TextField(choices=LinkStatus.choices)
    type = models.TextField(choices=LinkType.choices, default=None, blank=True, null=True)

    install_date = models.DateField(default=None, blank=True, null=True)
    abandon_date = models.DateField(default=None, blank=True, null=True)

    description = models.TextField(default=None, blank=True, null=True)
    notes = models.TextField(default=None, blank=True, null=True)


class Sector(models.Model):
    class SectorStatus(models.TextChoices):
        ABANDONED = "Abandoned"
        ACTIVE = "Active"
        POTENTIAL = "Potential"

    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    name = models.TextField()

    radius = models.FloatField(
        validators=[MinValueValidator(0)],
    )
    azimuth = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(360),
        ],
    )
    width = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(360),
        ],
    )

    status = models.TextField(choices=SectorStatus.choices)

    install_date = models.DateField(default=None, blank=True, null=True)
    abandon_date = models.DateField(default=None, blank=True, null=True)

    device_name = models.TextField()
    ssid = models.TextField(default=None, blank=True, null=True)

    notes = models.TextField(default=None, blank=True, null=True)
