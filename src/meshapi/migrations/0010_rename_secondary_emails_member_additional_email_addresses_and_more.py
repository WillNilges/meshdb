# Generated by Django 4.2.9 on 2024-02-15 23:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("meshapi", "0009_alter_install_install_status"),
    ]

    operations = [
        migrations.RenameField(
            model_name="member",
            old_name="secondary_emails",
            new_name="additional_email_addresses",
        ),
        migrations.RenameField(
            model_name="member",
            old_name="email_address",
            new_name="primary_email_address",
        ),
    ]
