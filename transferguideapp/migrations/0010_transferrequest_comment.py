# Generated by Django 4.1.6 on 2023-04-07 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0009_alter_transferrequest_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferrequest',
            name='comment',
            field=models.CharField(default='', max_length=200),
        ),
    ]
