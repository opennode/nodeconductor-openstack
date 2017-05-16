from django.conf import settings

import logging

from celery import shared_task
from django.template.loader import render_to_string

from nodeconductor.core import tasks as core_tasks, utils as core_utils

from .. import models

logger = logging.getLogger(__name__)


class TenantCreateErrorTask(core_tasks.ErrorStateTransitionTask):

    def execute(self, tenant):
        super(TenantCreateErrorTask, self).execute(tenant)
        # Delete network and subnet if they were not created on backend,
        # mark as erred if they were created
        network = tenant.networks.first()
        subnet = network.subnets.first()
        if subnet.state == models.SubNet.States.CREATION_SCHEDULED:
            subnet.delete()
        else:
            super(TenantCreateErrorTask, self).execute(subnet)
        if network.state == models.Network.States.CREATION_SCHEDULED:
            network.delete()
        else:
            super(TenantCreateErrorTask, self).execute(network)


class TenantCreateSuccessTask(core_tasks.StateTransitionTask):

    def execute(self, tenant):
        network = tenant.networks.first()
        subnet = network.subnets.first()
        self.state_transition(network, 'set_ok')
        self.state_transition(subnet, 'set_ok')
        self.state_transition(tenant, 'set_ok')
        return super(TenantCreateSuccessTask, self).execute(tenant)


class PollBackendCheckTask(core_tasks.Task):
    max_retries = 60
    default_retry_delay = 5

    @classmethod
    def get_description(cls, instance, backend_check_method, *args, **kwargs):
        return 'Check instance "%s" with method "%s"' % (instance, backend_check_method)

    def get_backend(self, instance):
        return instance.get_backend()

    def execute(self, instance, backend_check_method):
        # backend_check_method should return True if object does not exist at backend
        backend = self.get_backend(instance)
        if not getattr(backend, backend_check_method)(instance):
            self.retry()
        return instance


class TenantPullQuotas(core_tasks.BackgroundTask):
    name = 'openstack.TenantPullQuotas'

    def is_equal(self, other_task):
        return self.name == other_task.get('name')

    def run(self):
        from .. import executors
        for tenant in models.Tenant.objects.filter(state=models.Tenant.States.OK):
            executors.TenantPullQuotasExecutor.execute(tenant)
