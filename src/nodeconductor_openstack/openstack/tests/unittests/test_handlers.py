from django.test import TestCase
from mock import patch

from nodeconductor.core import utils as core_utils
from nodeconductor.structure import models as structure_models
from nodeconductor.structure.tests import factories as structure_factories

from .. import factories


@patch('nodeconductor.core.tasks.BackendMethodTask.delay')
class SshKeysHandlersTest(TestCase):

    def setUp(self):
        self.user = structure_factories.UserFactory()
        self.ssh_key = structure_factories.SshPublicKeyFactory(user=self.user)
        self.tenant = factories.TenantFactory()

    def test_ssh_key_will_be_removed_if_user_lost_connection_to_tenant(self, mocked_task_call):
        project = self.tenant.service_project_link.project
        project.add_user(self.user, structure_models.ProjectRole.ADMINISTRATOR)
        project.remove_user(self.user)

        serialized_tenant = core_utils.serialize_instance(self.tenant)
        mocked_task_call.assert_called_once_with(
            serialized_tenant, 'remove_ssh_key_from_tenant', self.ssh_key.name, self.ssh_key.fingerprint)

    def test_ssh_key_will_not_be_removed_if_user_still_has_connection_to_tenant(self, mocked_task_call):
        project = self.tenant.service_project_link.project
        project.add_user(self.user, structure_models.ProjectRole.ADMINISTRATOR)
        project.customer.add_user(self.user, structure_models.CustomerRole.OWNER)
        project.remove_user(self.user)

        self.assertEqual(mocked_task_call.call_count, 0)

    def test_ssh_key_will_be_deleted_from_tenant_on_user_deletion(self, mocked_task_call):
        project = self.tenant.service_project_link.project
        project.add_user(self.user, structure_models.ProjectRole.ADMINISTRATOR)
        self.user.delete()

        serialized_tenant = core_utils.serialize_instance(self.tenant)
        mocked_task_call.assert_called_once_with(
            serialized_tenant, 'remove_ssh_key_from_tenant', self.ssh_key.name, self.ssh_key.fingerprint)

    def test_ssh_key_will_be_deleted_from_tenant_on_ssh_key_deletion(self, mocked_task_call):
        project = self.tenant.service_project_link.project
        project.add_user(self.user, structure_models.ProjectRole.ADMINISTRATOR)
        self.ssh_key.delete()

        serialized_tenant = core_utils.serialize_instance(self.tenant)
        mocked_task_call.assert_called_once_with(
            serialized_tenant, 'remove_ssh_key_from_tenant', self.ssh_key.name, self.ssh_key.fingerprint)
