# Generated by Django 4.2.5 on 2023-12-23 03:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meshapi", "0018_rename_network_number_building_primary_nn_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="install",
            name="install_number",
            field=models.AutoField(db_column="install_number", primary_key=True, serialize=False),
        ),
    ]
