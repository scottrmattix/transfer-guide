# Generated by Django 4.1.6 on 2023-04-07 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0007_favorites_created_at_favorites_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferrequest',
            name='url',
            field=models.URLField(default=None),
        ),
    ]
