# Generated by Django 4.1.6 on 2023-03-19 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internalcourse',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
