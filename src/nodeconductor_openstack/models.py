from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible, force_text
from django_fsm import transition, FSMIntegerField
from jsonfield import JSONField
from iptools.ipv4 import validate_cidr
from model_utils import FieldTracker
from model_utils.models import TimeStampedModel
from urlparse import urlparse

from nodeconductor.core import models as core_models
from nodeconductor.logging.loggers import LoggableMixin
from nodeconductor.quotas.fields import QuotaField
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models
from nodeconductor.structure.utils import get_coordinates_by_ip, Coordinates

from .backup import BackupBackend, BackupScheduleBackend
from .managers import BackupManager


class OpenStackService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='openstack_services', through='OpenStackServiceProjectLink')

    class Meta:
        unique_together = ('customer', 'settings')
        verbose_name = 'OpenStack service'
        verbose_name_plural = 'OpenStack services'

    @classmethod
    def get_url_name(cls):
        return 'openstack'


class OpenStackServiceProjectLink(structure_models.ServiceProjectLink):

    service = models.ForeignKey(OpenStackService)

    class Meta(structure_models.ServiceProjectLink.Meta):
        verbose_name = 'OpenStack service project link'
        verbose_name_plural = 'OpenStack service project links'

    @classmethod
    def get_url_name(cls):
        return 'openstack-spl'

    # XXX: Hack for statistics: return quotas of tenants as quotas of SPLs.
    @classmethod
    def get_sum_of_quotas_as_dict(cls, spls, quota_names=None, fields=['usage', 'limit']):
        tenants = Tenant.objects.filter(service_project_link__in=spls)
        return Tenant.get_sum_of_quotas_as_dict(tenants, quota_names=quota_names, fields=fields)


class Flavor(LoggableMixin, structure_models.ServiceProperty):
    cores = models.PositiveSmallIntegerField(help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(help_text='Root disk size in MiB')


class Image(structure_models.ServiceProperty):
    min_disk = models.PositiveIntegerField(default=0, help_text='Minimum disk size in MiB')
    min_ram = models.PositiveIntegerField(default=0, help_text='Minimum memory size in MiB')


@python_2_unicode_compatible
class SecurityGroup(core_models.UuidMixin,
                    core_models.NameMixin,
                    core_models.DescribableMixin,
                    core_models.StateMixin):

    class Permissions(object):
        customer_path = 'service_project_link__project__customer'
        project_path = 'service_project_link__project'
        project_group_path = 'service_project_link__project__project_groups'

    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='security_groups')
    tenant = models.ForeignKey('Tenant', related_name='security_groups')

    backend_id = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.service_project_link)

    def get_backend(self):
        return self.tenant.get_backend()

    @classmethod
    def get_url_name(cls):
        return 'openstack-sgp'


@python_2_unicode_compatible
class SecurityGroupRule(models.Model):
    TCP = 'tcp'
    UDP = 'udp'
    ICMP = 'icmp'

    CHOICES = (
        (TCP, 'tcp'),
        (UDP, 'udp'),
        (ICMP, 'icmp'),
    )

    security_group = models.ForeignKey(SecurityGroup, related_name='rules')
    protocol = models.CharField(max_length=4, blank=True, choices=CHOICES)
    from_port = models.IntegerField(validators=[MaxValueValidator(65535)], null=True)
    to_port = models.IntegerField(validators=[MaxValueValidator(65535)], null=True)
    cidr = models.CharField(max_length=32, blank=True)

    backend_id = models.CharField(max_length=128, blank=True)

    def validate_icmp(self):
        if self.from_port is not None and not -1 <= self.from_port <= 255:
            raise ValidationError('Wrong value for "from_port": '
                                  'expected value in range [-1, 255], found %d' % self.from_port)
        if self.to_port is not None and not -1 <= self.to_port <= 255:
            raise ValidationError('Wrong value for "to_port": '
                                  'expected value in range [-1, 255], found %d' % self.to_port)

    def validate_port(self):
        if self.from_port is not None and self.to_port is not None:
            if self.from_port > self.to_port:
                raise ValidationError('"from_port" should be less or equal to "to_port"')
        if self.from_port is not None and self.from_port < 1:
            raise ValidationError('Wrong value for "from_port": '
                                  'expected value in range [1, 65535], found %d' % self.from_port)
        if self.to_port is not None and self.to_port < 1:
            raise ValidationError('Wrong value for "to_port": '
                                  'expected value in range [1, 65535], found %d' % self.to_port)

    def validate_cidr(self):
        if not self.cidr:
            return

        if not validate_cidr(self.cidr):
            raise ValidationError(
                'Wrong cidr value. Expected cidr format: <0-255>.<0-255>.<0-255>.<0-255>/<0-32>')

    def clean(self):
        if self.protocol == 'icmp':
            self.validate_icmp()
        elif self.protocol in ('tcp', 'udp'):
            self.validate_port()
        else:
            raise ValidationError('Wrong value for "protocol": '
                                  'expected one of (tcp, udp, icmp), found %s' % self.protocol)
        self.validate_cidr()

    def __str__(self):
        return '%s (%s): %s (%s -> %s)' % \
               (self.security_group, self.protocol, self.cidr, self.from_port, self.to_port)


class IpMapping(core_models.UuidMixin):

    class Permissions(object):
        project_path = 'project'
        customer_path = 'project__customer'
        project_group_path = 'project__project_groups'

    public_ip = models.GenericIPAddressField(protocol='IPv4')
    private_ip = models.GenericIPAddressField(protocol='IPv4')
    project = models.ForeignKey(structure_models.Project, related_name='+')


class FloatingIP(core_models.UuidMixin):

    class Permissions(object):
        customer_path = 'service_project_link__project__customer'
        project_path = 'service_project_link__project'
        project_group_path = 'service_project_link__project__project_groups'

    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='floating_ips')
    tenant = models.ForeignKey('Tenant', related_name='floating_ips')

    address = models.GenericIPAddressField(protocol='IPv4')
    status = models.CharField(max_length=30)
    backend_id = models.CharField(max_length=255)
    backend_network_id = models.CharField(max_length=255, editable=False)

    tracker = FieldTracker()

    def get_backend(self):
        return self.tenant.get_backend()


class Instance(structure_models.VirtualMachineMixin,
               structure_models.PaidResource,
               structure_models.Resource):

    DEFAULT_DATA_VOLUME_SIZE = 20 * 1024

    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='instances', on_delete=models.PROTECT)

    # OpenStack backend specific fields
    system_volume_id = models.CharField(max_length=255, blank=True)
    system_volume_size = models.PositiveIntegerField(default=0, help_text='Root disk size in MiB')
    data_volume_id = models.CharField(max_length=255, blank=True)
    data_volume_size = models.PositiveIntegerField(
        default=DEFAULT_DATA_VOLUME_SIZE, help_text='Data disk size in MiB', validators=[MinValueValidator(1 * 1024)])

    flavor_name = models.CharField(max_length=255, blank=True)
    flavor_disk = models.PositiveIntegerField(default=0, help_text='Flavor disk size in MiB')

    tracker = FieldTracker()
    tenant = models.ForeignKey('Tenant', related_name='instances')

    def get_backend(self):
        return self.tenant.get_backend()

    # XXX: For compatibility with new-style state.
    @property
    def human_readable_state(self):
        return force_text(dict(self.States.CHOICES)[self.state])

    @classmethod
    def get_url_name(cls):
        return 'openstack-instance'

    def get_log_fields(self):
        return (
            'uuid', 'name', 'type', 'service_project_link', 'ram', 'cores',
            'data_volume_size', 'system_volume_size',
        )

    def detect_coordinates(self):
        settings = self.service_project_link.service.settings
        data = settings.get_option('coordinates')
        if data:
            return Coordinates(latitude=data['latitude'],
                               longitude=data['longitude'])
        else:
            hostname = urlparse(settings.backend_url).hostname
            if hostname:
                return get_coordinates_by_ip(hostname)

    def increase_backend_quotas_usage(self, validate=True):
        add_quota = self.tenant.add_quota_usage
        add_quota('instances', 1)
        add_quota('ram', self.ram)
        add_quota('vcpu', self.cores)
        add_quota('storage', self.disk)

    def decrease_backend_quotas_usage(self):
        add_quota = self.tenant.add_quota_usage
        add_quota('instances', -1)
        add_quota('ram', -self.ram)
        add_quota('vcpu', -self.cores)
        add_quota('storage', -self.disk)


class InstanceSecurityGroup(models.Model):

    class Permissions(object):
        project_path = 'instance__project'
        project_group_path = 'instance__project__project_groups'

    instance = models.ForeignKey(Instance, related_name='security_groups')
    security_group = models.ForeignKey(SecurityGroup, related_name='instance_groups')


class BackupSchedule(core_models.UuidMixin,
                     core_models.DescribableMixin,
                     core_models.ScheduleMixin,
                     LoggableMixin):

    class Permissions(object):
        customer_path = 'instance__service_project_link__project__customer'
        project_path = 'instance__service_project_link__project'
        project_group_path = 'instance__service_project_link__project__project_groups'

    instance = models.ForeignKey(Instance, related_name='backup_schedules')
    retention_time = models.PositiveIntegerField(
        help_text='Retention time in days')  # if 0 - backup will be kept forever
    maximal_number_of_backups = models.PositiveSmallIntegerField()

    def __str__(self):
        return 'BackupSchedule of %s. Active: %s' % (self.instance, self.is_active)

    @classmethod
    def get_url_name(cls):
        return 'openstack-schedule'

    def get_backend(self):
        return BackupScheduleBackend(self)


class Backup(core_models.UuidMixin,
             core_models.DescribableMixin,
             LoggableMixin):

    class Permissions(object):
        customer_path = 'instance__service_project_link__project__customer'
        project_path = 'instance__service_project_link__project'
        project_group_path = 'instance__service_project_link__project__project_groups'

    class States(object):
        READY = 1
        BACKING_UP = 2
        RESTORING = 3
        DELETING = 4
        ERRED = 5
        DELETED = 6

        CHOICES = (
            (READY, 'Ready'),
            (BACKING_UP, 'Backing up'),
            (RESTORING, 'Restoring'),
            (DELETING, 'Deleting'),
            (ERRED, 'Erred'),
            (DELETED, 'Deleted'),
        )

    instance = models.ForeignKey(Instance, related_name='backups')
    backup_schedule = models.ForeignKey(BackupSchedule, blank=True, null=True,
                                        on_delete=models.SET_NULL,
                                        related_name='backups')
    kept_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Guaranteed time of backup retention. If null - keep forever.')

    created_at = models.DateTimeField(auto_now_add=True)

    state = FSMIntegerField(default=States.READY, choices=States.CHOICES)
    metadata = JSONField(
        blank=True,
        help_text='Additional information about backup, can be used for backup restoration or deletion',
    )

    objects = BackupManager()

    def __str__(self):
        return 'Backup of %s (%s)' % (self.instance, self.state)

    def get_backend(self):
        return BackupBackend(self)

    @classmethod
    def get_url_name(cls):
        return 'openstack-backup'

    @transition(field=state, source=States.READY, target=States.BACKING_UP)
    def starting_backup(self):
        pass

    @transition(field=state, source=States.BACKING_UP, target=States.READY)
    def confirm_backup(self):
        pass

    @transition(field=state, source=States.READY, target=States.RESTORING)
    def starting_restoration(self):
        pass

    @transition(field=state, source=States.RESTORING, target=States.READY)
    def confirm_restoration(self):
        pass

    @transition(field=state, source=States.READY, target=States.DELETING)
    def starting_deletion(self):
        pass

    @transition(field=state, source=States.DELETING, target=States.DELETED)
    def confirm_deletion(self):
        pass

    @transition(field=state, source='*', target=States.ERRED)
    def set_erred(self):
        pass


class Tenant(QuotaModelMixin, core_models.RuntimeStateMixin,
             structure_models.PrivateCloudMixin, structure_models.NewResource):

    class Quotas(QuotaModelMixin.Quotas):
        vcpu = QuotaField(default_limit=20, is_backend=True)
        ram = QuotaField(default_limit=51200, is_backend=True)
        storage = QuotaField(default_limit=1024000, is_backend=True)
        backup_storage = QuotaField(default_limit=1024000, is_backend=True)
        instances = QuotaField(default_limit=30, is_backend=True)
        security_group_count = QuotaField(default_limit=100, is_backend=True)
        security_group_rule_count = QuotaField(default_limit=100, is_backend=True)
        floating_ip_count = QuotaField(default_limit=50, is_backend=True)
        volumes = QuotaField(default_limit=50, is_backend=True)
        snapshots = QuotaField(default_limit=50, is_backend=True)

    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='tenants', on_delete=models.PROTECT)

    internal_network_id = models.CharField(max_length=64, blank=True)
    external_network_id = models.CharField(max_length=64, blank=True)
    availability_zone = models.CharField(
        max_length=100, blank=True,
        help_text='Optional availability group. Will be used for all instances provisioned in this tenant'
    )
    user_username = models.CharField(max_length=50, blank=True)
    user_password = models.CharField(max_length=50, blank=True)

    tracker = FieldTracker()

    def get_backend(self):
        return self.service_project_link.service.get_backend(tenant_id=self.backend_id)


class Volume(core_models.RuntimeStateMixin, structure_models.NewResource):
    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='volumes', on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, related_name='volumes')
    size = models.PositiveIntegerField(help_text='Size in MiB')
    bootable = models.BooleanField(default=False)
    metadata = JSONField(blank=True)
    image = models.ForeignKey(Image, null=True)
    image_metadata = JSONField(blank=True)
    type = models.CharField(max_length=100, blank=True)
    source_snapshot = models.ForeignKey('Snapshot', related_name='volumes', null=True, on_delete=models.SET_NULL)

    def get_backend(self):
        return self.tenant.get_backend()

    def increase_backend_quotas_usage(self, validate=True):
        self.tenant.add_quota_usage(Tenant.Quotas.volumes, 1, validate=validate)
        self.tenant.add_quota_usage(Tenant.Quotas.storage, self.size, validate=validate)

    def decrease_backend_quotas_usage(self):
        self.tenant.add_quota_usage(Tenant.Quotas.volumes, -1)
        self.tenant.add_quota_usage(Tenant.Quotas.storage, -self.size)


@python_2_unicode_compatible
class VolumeBackupRecord(core_models.UuidMixin, models.Model):
    """ Record that corresponds backup in swift.
        Several backups from OpenStack can be related to one record.
    """
    service = models.CharField(max_length=200)
    details = JSONField(blank=True)

    def __str__(self):
        name = '%s %s' % (self.details.get('display_name'), self.details.get('volume_id'))
        if not name.strip():
            return '(no data)'
        return name


class VolumeBackup(core_models.RuntimeStateMixin, structure_models.NewResource):
    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='volume_backups', on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, related_name='volume_backups')
    source_volume = models.ForeignKey(Volume, related_name='backups', null=True, on_delete=models.SET_NULL)
    size = models.PositiveIntegerField(help_text='Size of source volume in MiB')
    metadata = JSONField(blank=True, help_text='Information about volume that will be used on restoration')
    record = models.ForeignKey(VolumeBackupRecord, related_name='volume_backups', null=True, on_delete=models.SET_NULL)

    def get_backend(self):
        return self.tenant.get_backend()

    def increase_backend_quotas_usage(self, validate=True):
        self.tenant.add_quota_usage(Tenant.Quotas.backup_storage, self.size, validate=validate)

    def decrease_backend_quotas_usage(self):
        self.tenant.add_quota_usage(Tenant.Quotas.backup_storage, -self.size)


# For now this model has no endpoint, so there is not need to add permissions definition.
class VolumeBackupRestoration(core_models.UuidMixin, TimeStampedModel):
    """ This model corresponds volume restoration from backup.

        Stores restoration details:
         - mirrored backup, that is created from source backup.
         - volume - restored volume.
    """
    tenant = models.ForeignKey(Tenant, related_name='volume_backup_restorations')
    volume_backup = models.ForeignKey(VolumeBackup, related_name='restorations')
    mirorred_volume_backup = models.ForeignKey(VolumeBackup, related_name='+', null=True, on_delete=models.SET_NULL)
    volume = models.OneToOneField(Volume, related_name='+')

    def get_backend(self):
        return self.tenant.get_backend()


class Snapshot(core_models.RuntimeStateMixin, structure_models.NewResource):
    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='snapshots', on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, related_name='snapshots')
    # TODO: protect source_volume after NC-1410 implementation
    source_volume = models.ForeignKey(Volume, related_name='snapshots', null=True, on_delete=models.SET_NULL)
    size = models.PositiveIntegerField(help_text='Size in MiB')
    metadata = JSONField(blank=True)

    def get_backend(self):
        return self.tenant.get_backend()

    def increase_backend_quotas_usage(self, validate=True):
        self.tenant.add_quota_usage(Tenant.Quotas.snapshots, 1, validate=validate)
        self.tenant.add_quota_usage(Tenant.Quotas.storage, self.size, validate=validate)

    def decrease_backend_quotas_usage(self):
        self.tenant.add_quota_usage(Tenant.Quotas.snapshots, -1)
        self.tenant.add_quota_usage(Tenant.Quotas.storage, -self.size)


# XXX: This model is itacloud specific, it should be moved to assembly
class DRBackup(core_models.RuntimeStateMixin, structure_models.NewResource):
    service_project_link = models.ForeignKey(
        OpenStackServiceProjectLink, related_name='dr_backups', on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, related_name='dr_backups')
    source_instance = models.ForeignKey(Instance, related_name='dr_backups', null=True, on_delete=models.SET_NULL)
    metadata = JSONField(
        blank=True,
        help_text='Information about instance that will be used on restoration',
    )
    # XXX: This field is temporary. Should be deleted in NC-1410.
    instance_volumes = models.ManyToManyField(Volume, related_name='+')
    temporary_volumes = models.ManyToManyField(Volume, related_name='+')
    temporary_snapshots = models.ManyToManyField(Snapshot, related_name='+')
    volume_backups = models.ManyToManyField(VolumeBackup, related_name='dr_backups')

    def get_backend(self):
        return self.tenant.get_backend()


# XXX: This model is itacloud specific, it should be moved to assembly
class DRBackupRestoration(core_models.UuidMixin, core_models.RuntimeStateMixin, TimeStampedModel):
    """ This model corresponds instance restoration from DR backup.

        Stores restoration details:
         - volume_backup_restorations - restoration details of each instance volume.
         - instance - restored instance.
    """
    dr_backup = models.ForeignKey(DRBackup, related_name='restorations')
    instance = models.OneToOneField(Instance, related_name='+')
    tenant = models.ForeignKey(Tenant, related_name='+', help_text='Tenant for instance restoration')
    flavor = models.ForeignKey(Flavor, related_name='+')
    volume_backup_restorations = models.ManyToManyField(VolumeBackupRestoration, related_name='+')

    class Permissions(object):
        customer_path = 'dr_backup__service_project_link__project__customer'
        project_path = 'dr_backup__service_project_link__project'
        project_group_path = 'dr_backup__service_project_link__project__project_groups'

    def get_backend(self):
        return self.tenant.get_backend()

    @classmethod
    def get_url_name(cls):
        return 'openstack-dr-backup'