# Generated by Django 4.2.5 on 2023-10-13 07:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meshapi", "0011_alter_building_bin"),
    ]

    operations = [
        migrations.AlterField(
            model_name="building",
            name="network_number",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]