# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-28 21:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0003_buildresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='tag',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
