# Generated by Django 4.1.6 on 2023-04-07 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0002_notification_transferrequest_delete_notificaion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='notifcation',
            new_name='notification',
        ),
    ]
