# Generated by Django 5.2.1 on 2025-06-12 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_semester_name_alter_semester_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
    ]
