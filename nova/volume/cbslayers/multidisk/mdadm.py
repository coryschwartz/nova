# Cory Schwartz

import os

from oslo_log import log as logging

from nova import exception
from nova import utils
from nova.volume.cbslayers import base


LOG = logging.getLogger(__name__)


class Raid5(base.LayeredVolume):
    """
    A 'highly-available' volume distributed using mdadm/RAID-5
    """

    def __init__(self, connection_info, **kwargs):
        # Fail if no device_path was set when connecting the volume, e.g. in
        # the case of libvirt network volume drivers.
        data = connection_info['data']
        if not data.get('device_path'):
            volume_id = data.get('volume_id') or connection_info.get('serial')
            raise exception.VolumeEncryptionNotSupported(
                volume_id=volume_id,
                volume_type=connection_info['driver_volume_type'])

        # the device's path as given to libvirt -- e.g., /dev/disk/by-path/...
        self.symlink_path = connection_info['data']['device_path']

        # a unique name for the volume -- e.g., the iSCSI participant name
        self.dev_name = self.symlink_path.split('/')[-1]
        # the device's actual path on the compute host -- e.g., /dev/sd_
        self.dev_path = os.path.realpath(self.symlink_path)

    def _assemble_volume(self, raiduuid, **kwargs):
        """
        Assembles volumes into a raid configuration
        :param vollist : A list of volumes used for assembly.
        """
        LOG.debug("Assembling RAID volume %s", voluuid)

        cmd = ["mdadm", "--assemble", "uuid=%s" % raiduuid ]

        utils.execute(*cmd, check_exit_code=True, run_as_root=True)

    def attach_volume(self, context, **kwargs):
        """Shadows the device and passes an assembled version to the
        instance.
        """

        self._assemble_volume(passphrase, **kwargs)

        # modify the original symbolic link to refer to the assembled device
        utils.execute('ln', '--symbolic', '--force',
                      '/dev/mapper/%s' % self.dev_name, self.symlink_path,
                      run_as_root=True, check_exit_code=True)

    def _stop_volume(self, **kwargs):
        """Closes the device (effectively removes the dm-crypt mapping)."""
        LOG.debug("stopping RAID volume %s", self.dev_path)
        utils.execute('mdadm', '--stop', self.dev_name,
                      run_as_root=True, check_exit_code=True)

    def detach_volume(self, **kwargs):
        """Removes the dm-crypt mapping for the device."""
        self._stop_volume(**kwargs)
