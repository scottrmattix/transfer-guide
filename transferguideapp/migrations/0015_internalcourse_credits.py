# Generated by Django 4.1.7 on 2023-04-11 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transferguideapp', '0014_remove_internalcourse_credits'),
    ]

    operations = [
        migrations.AddField(
            model_name='internalcourse',
            name='credits',
            field=models.CharField(default=-1, max_length=30),
        ),
    ]