# Generated by Django 4.1.6 on 2023-04-07 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0008_transferrequest_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferrequest',
            name='url',
            field=models.URLField(default=''),
        ),
    ]
