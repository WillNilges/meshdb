# Generated by Django 4.2.5 on 2023-09-12 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
#    replaces = [
#        ("meshapi", "0001_initial"),
#        ("meshapi", "0002_remove_building_panorama_image_install_abandon_date_and_more"),
#        ("meshapi", "0003_alter_request_install_id"),
#    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Building",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("bin", models.IntegerField()),
                ("building_status", models.IntegerField(choices=[(0, "Inactive"), (1, "Active")])),
                ("street_address", models.TextField()),
                ("city", models.TextField()),
                ("state", models.TextField()),
                ("zip_code", models.IntegerField()),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("altitude", models.FloatField()),
                ("network_number", models.IntegerField()),
                ("install_date", models.DateField(blank=True, default=None, null=True)),
                ("abandon_date", models.DateField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("first_name", models.TextField()),
                ("last_name", models.TextField()),
                ("email_address", models.EmailField(max_length=254)),
                ("phone_numer", models.TextField(blank=True, default=None, null=True)),
                ("slack_handle", models.TextField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Install",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("install_number", models.IntegerField()),
                ("install_status", models.IntegerField(choices=[(0, "Planned"), (1, "Inactive"), (2, "Active")])),
                ("building_id", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="meshapi.building")),
                ("member_id", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="meshapi.member")),
                ("abandon_date", models.DateField(blank=True, default=None, null=True)),
                ("install_date", models.DateField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Request",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("request_status", models.IntegerField(choices=[(0, "Open"), (1, "Closed"), (2, "Installed")])),
                ("ticket_id", models.IntegerField()),
                ("building_id", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="meshapi.building")),
                (
                    "install_id",
                    models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to="meshapi.install"),
                ),
                ("member_id", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="meshapi.member")),
            ],
        ),
    ]
