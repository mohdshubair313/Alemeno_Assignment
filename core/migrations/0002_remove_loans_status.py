# Generated by Django 5.2.1 on 2025-06-02 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loans',
            name='status',
        ),
    ]
