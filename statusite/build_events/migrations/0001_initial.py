# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-29 19:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('repository', '0003_release_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_name', models.CharField(max_length=255)),
                ('mbci_build_id', models.IntegerField(verbose_name='mrbelvedereci build id')),
                ('status', models.CharField(max_length=25)),
                ('build_date', models.DateField()),
                ('tests_passed', models.IntegerField()),
                ('tests_failed', models.IntegerField()),
                ('tests_total', models.IntegerField()),
                ('build_data', jsonfield.fields.JSONField()),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_results', to='repository.Release')),
                ('repo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='build_results', to='repository.Repository')),
            ],
            options={
                'verbose_name': 'Build Result',
            },
        ),
    ]
