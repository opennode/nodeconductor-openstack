# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-18 15:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openstack_tenant', '0032_nullable_internal_ip_instance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='backend_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='instance',
            unique_together=set([('service_project_link', 'backend_id')]),
        ),
        migrations.AlterField(
            model_name='snapshot',
            name='backend_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='volume',
            name='backend_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='snapshot',
            unique_together=set([('service_project_link', 'backend_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='volume',
            unique_together=set([('service_project_link', 'backend_id')]),
        ),
    ]
