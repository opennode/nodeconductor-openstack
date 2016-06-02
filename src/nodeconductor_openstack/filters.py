import django_filters

from nodeconductor.core import filters as core_filters
from nodeconductor.structure import filters as structure_filters

from . import models


class OpenStackServiceProjectLinkFilter(structure_filters.BaseServiceProjectLinkFilter):
    service = core_filters.URLFilter(view_name='openstack-detail', name='service__uuid')

    class Meta(object):
        model = models.OpenStackServiceProjectLink


class InstanceFilter(structure_filters.BaseResourceFilter):

    class Meta(structure_filters.BaseResourceFilter.Meta):
        model = models.Instance
        order_by = structure_filters.BaseResourceFilter.Meta.order_by + [
            'ram',
            '-ram',
            'cores',
            '-cores',
            'system_volume_size',
            '-system_volume_size',
            'data_volume_size',
            '-data_volume_size',
        ]
        order_by_mapping = dict(
            # Backwards compatibility
            project__customer__name='service_project_link__project__customer__name',
            project__name='service_project_link__project__name',
            project__project_groups__name='service_project_link__project__project_groups__name',

            **structure_filters.BaseResourceFilter.Meta.order_by_mapping
        )


class SecurityGroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        name='name',
        lookup_type='icontains',
    )
    description = django_filters.CharFilter(
        name='description',
        lookup_type='icontains',
    )
    service = django_filters.CharFilter(
        name='service_project_link__service__uuid',
    )
    project = django_filters.CharFilter(
        name='service_project_link__project__uuid',
    )
    settings_uuid = django_filters.CharFilter(
        name='service_project_link__service__settings__uuid'
    )
    service_project_link = core_filters.URLFilter(
        view_name='openstack-spl-detail',
        name='service_project_link__pk',
        lookup_field='pk',
    )
    tenant_uuid = django_filters.CharFilter(
        name='tenant__uuid'
    )
    state = core_filters.StateFilter()

    class Meta(object):
        model = models.SecurityGroup
        fields = [
            'name',
            'description',
            'service',
            'project',
            'service_project_link',
            'state',
        ]


class IpMappingFilter(django_filters.FilterSet):
    project = django_filters.CharFilter(name='project__uuid')

    # XXX: remove after upgrading to django-filter 0.12
    #      which is still unavailable at https://pypi.python.org/simple/django-filter/
    private_ip = django_filters.CharFilter()
    public_ip = django_filters.CharFilter()

    class Meta(object):
        model = models.IpMapping
        fields = [
            'project',
            'private_ip',
            'public_ip',
        ]


class FloatingIPFilter(django_filters.FilterSet):
    project = django_filters.CharFilter(
        name='service_project_link__project__uuid',
    )
    service = django_filters.CharFilter(
        name='service_project_link__service__uuid',
    )
    service_project_link = core_filters.URLFilter(
        view_name='openstack-spl-detail',
        name='service_project_link__pk',
        lookup_field='pk',
    )

    class Meta(object):
        model = models.FloatingIP
        fields = [
            'project',
            'service',
            'status',
            'service_project_link',
        ]


class FlavorFilter(structure_filters.ServicePropertySettingsFilter):

    class Meta(structure_filters.ServicePropertySettingsFilter.Meta):
        model = models.Flavor
        fields = dict({
            'cores': ['exact', 'gte', 'lte'],
            'ram': ['exact', 'gte', 'lte'],
            'disk': ['exact', 'gte', 'lte'],
        }, **{field: ['exact'] for field in structure_filters.ServicePropertySettingsFilter.Meta.fields})
        order_by = [
            'cores',
            '-cores',
            'ram',
            '-ram',
            'disk',
            '-disk',
        ]


class BackupScheduleFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(
        lookup_type='icontains',
    )

    class Meta(object):
        model = models.BackupSchedule
        fields = (
            'description',
        )


class BackupFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(
        lookup_type='icontains',
    )
    instance = django_filters.CharFilter(
        name='instance__uuid',
    )
    project = django_filters.CharFilter(
        name='instance__service_project_link__project__uuid',
    )

    class Meta(object):
        model = models.Backup
        fields = (
            'description',
            'instance',
            'project',
        )
