# Generated by Django 2.0.1 on 2018-02-09 04:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp', '0009_remove_response_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='response',
            name='question',
        ),
    ]