# Generated by Django 4.1.5 on 2023-03-18 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
            ],
        ),

        migrations.CreateModel(
            name='ExternalCollege',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('college_name', models.CharField(max_length=60)),
                ('domestic_college', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='InternalCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mnemonic', models.CharField(max_length=30)),
                ('course_number', models.CharField(max_length=30)),
                ('course_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mnemonic', models.CharField(max_length=20)),
                ('course_number', models.CharField(max_length=20)),
                ('course_name', models.CharField(max_length=200)),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transferguideapp.externalcollege')),
            ],
        ),
        migrations.CreateModel(
            name='CourseTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('external_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transferguideapp.externalcourse')),
                ('internal_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transferguideapp.internalcourse')),
            ],
        ),
    ]
