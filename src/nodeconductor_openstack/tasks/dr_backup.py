from nodeconductor.core import tasks

from . import models


class SetDRBackupErredTask(tasks.ErrorStateTransitionTask):
    """ Mark DR backup and all related resources that are not in state OK as Erred """

    def execute(self, dr_backup):
        super(SetDRBackupErredTask, self).execute(dr_backup)
        ok_state = models.DRBackup.States.OK
        creation_scheduled_state = models.DRBackup.States.CREATION_SCHEDULED
        related_resources = (
            list(dr_backup.temporary_volumes.exclude(state=ok_state)) +
            list(dr_backup.temporary_snapshots.exclude(state=ok_state)) +
            list(dr_backup.volume_backups.exclude(state=ok_state))
        )
        for resource in related_resources:
            # If resource creation was not started - delete it from NC DB.
            if resource.state == creation_scheduled_state:
                resource.decrease_backend_quotas_usage()
                resource.delete()
            else:
                resource.set_erred()
                resource.save(update_fields=['state'])

        # Deactivate schedule if its backup become erred.
        schedule = dr_backup.backup_schedule
        if schedule:
            schedule.error_message = 'Failed to execute backup for %s. Error: %s' % (
                dr_backup.instance, dr_backup.error_message)
            schedule.runtime_state = 'Failed to create backup'
            schedule.is_active = False
            schedule.save()


class CleanUpDRBackupTask(tasks.StateTransitionTask):
    """ Mark DR backup as OK and delete related resources.

        Celery is too fragile with groups or chains in callback.
        It is safer to make cleanup in one task.
    """
    def execute(self, dr_backup, force=False):
        # import here to avoid circular dependencies
        from ..executors import SnapshotDeleteExecutor, VolumeDeleteExecutor
        for snapshot in dr_backup.temporary_snapshots.all():
            SnapshotDeleteExecutor.execute(snapshot, force=force)
        for volume in dr_backup.temporary_volumes.all():
            VolumeDeleteExecutor.execute(volume, force=force)


class ForceDeleteDRBackupTask(tasks.StateTransitionTask):

    def execute(self, dr_backup):
        dr_backup.volume_backups.all().delete()
        dr_backup.delete()
