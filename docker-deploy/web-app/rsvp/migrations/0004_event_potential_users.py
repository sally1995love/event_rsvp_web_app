# Generated by Django 2.0.1 on 2018-02-07 02:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rsvp', '0003_auto_20180203_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='potential_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
