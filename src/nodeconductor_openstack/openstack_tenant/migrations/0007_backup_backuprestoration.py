# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import nodeconductor.logging.loggers
import jsonfield.fields
import model_utils.fields
import nodeconductor.core.fields
import nodeconductor.core.models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers
import django_fsm
import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('openstack_tenant', '0006_resource_action_details'),
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
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
                ('kept_until', models.DateTimeField(help_text=b'Guaranteed time of backup retention. If null - keep forever.', null=True, blank=True)),
                ('metadata', jsonfield.fields.JSONField(help_text=b'Additional information about backup, can be used for backup restoration or deletion', blank=True)),
                ('instance', models.ForeignKey(related_name='backups', on_delete=django.db.models.deletion.PROTECT, to='openstack_tenant.Instance')),
                ('service_project_link', models.ForeignKey(related_name='backups', on_delete=django.db.models.deletion.PROTECT, to='openstack_tenant.OpenStackTenantServiceProjectLink')),
                ('snapshots', models.ManyToManyField(related_name='backups', to='openstack_tenant.Snapshot')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=(nodeconductor.core.models.SerializableAbstractMixin, nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BackupRestoration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backup', models.ForeignKey(related_name='restorations', to='openstack_tenant.Backup')),
                ('flavor', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='openstack_tenant.Flavor', null=True)),
                ('instance', models.OneToOneField(related_name='+', to='openstack_tenant.Instance')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
