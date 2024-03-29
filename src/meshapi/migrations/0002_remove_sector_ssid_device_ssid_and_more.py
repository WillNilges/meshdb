# Generated by Django 4.2.10 on 2024-03-16 17:11

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meshapi", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sector",
            name="ssid",
        ),
        migrations.AddField(
            model_name="device",
            name="ssid",
            field=models.CharField(
                blank=True, default=None, help_text="The SSID being broadcast by this device", null=True
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="address_truth_sources",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("OSMNominatim", "OSMNominatim"),
                        ("OSMNominatimZIPOnly", "OSMNominatimZIPOnly"),
                        ("NYCPlanningLabs", "NYCPlanningLabs"),
                        ("PeliasStringParsing", "PeliasStringParsing"),
                        ("ReverseGeocodeFromCoordinates", "ReverseGeocodeFromCoordinates"),
                    ]
                ),
                help_text="A list of strings that answers the question: How was the content ofthe street address, city, state, and ZIP fields determined? This is useful in understanding the level of validation applied to spreadsheet imported data. Possible values are: OSMNominatim, OSMNominatimZIPOnly, NYCPlanningLabs, PeliasStringParsing, ReverseGeocodeFromCoordinates. Check the import script for details",
                size=None,
            ),
        ),
    ]
