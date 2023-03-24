# Generated by Django 4.1.7 on 2023-03-24 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transferguideapp', '0003_favorites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_items', to=settings.AUTH_USER_MODEL),
        ),
    ]
