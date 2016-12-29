# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import nodeconductor.logging.loggers
import django.utils.timezone
import model_utils.fields
import nodeconductor.core.fields
import nodeconductor.core.models
import django.db.models.deletion
import taggit.managers
import django_fsm
import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('openstack', '0024_internalnetwork'),
    ]

    operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('state', django_fsm.FSMIntegerField(default=5, choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')])),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('is_external', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=50, blank=True)),
                ('segmentation_id', models.IntegerField(null=True)),
                ('service_project_link', models.ForeignKey(related_name='internal_networks', on_delete=django.db.models.deletion.PROTECT, to='openstack.OpenStackServiceProjectLink')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
                ('tenant', models.ForeignKey(related_name='internal_networks', to='openstack.Tenant')),
            ],
            options={
                'abstract': False,
            },
            bases=(nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.RemoveField(
            model_name='internalnetwork',
            name='service_project_link',
        ),
        migrations.RemoveField(
            model_name='internalnetwork',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='internalnetwork',
            name='tenant',
        ),
        migrations.DeleteModel(
            name='InternalNetwork',
        ),
    ]
