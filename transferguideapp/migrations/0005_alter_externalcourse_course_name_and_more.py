# Generated by Django 4.1.6 on 2023-03-18 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0004_externalcollege_internalcourse_externalcourse_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalcourse',
            name='course_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='externalcourse',
            name='course_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='externalcourse',
            name='mnemonic',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='internalcourse',
            name='course_name',
            field=models.CharField(max_length=200),
        ),
    ]
