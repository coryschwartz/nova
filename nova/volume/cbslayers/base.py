#    Cory Schwartz

import abc
import six

@six.add_metaclass(abc.ABCMeta)
class LayeredVolume(object):
    """Base class to support Layered Volumes.
    Base class for encrypted and multi-disk volumes
    performs no actions for either hook.
    """

    @abc.abstractmethod
    def attach_volume(self, context, **kwargs):
        """Hook called immediately prior to attaching a volume to an instance.
        """
        pass

    @abc.abstractmethod
    def detach_volume(self, **kwargs):
        """Hook called immediately after detaching a volume from an instance.
        """
        pass
