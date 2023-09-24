# Generated by Django 4.2.5 on 2023-10-09 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meshapi", "0004_installer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="request",
            name="install_id",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="meshapi.install"
            ),
        ),
    ]
