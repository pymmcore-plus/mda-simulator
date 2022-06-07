from numbers import Real

import numpy as np
from pymmcore_plus import CMMCorePlus
from pymmcore_plus._util import _qt_app_is_running
from qtpy.QtCore import QTimer
from wrapt import synchronized

from mda_simulator import ImageGenerator

__all__ = ["ChannelTracker", "FakeDemoCamera"]


class ChannelTracker:
    """
    Simple version of hte preset widget to track the current channel.

    Doesn't update if the individual components all get switched like
    the preset widget does. Probably doesn't matter much for this use case.
    """

    def __init__(self, group: str = None, core: CMMCorePlus = None):
        """
        Parameters
        ----------
        group : str
            The channelGroup to use. If not provided we will get
            from the core.
        core : CMMCorePlus
        """
        self._core = core or CMMCorePlus.instance()
        self._core.events.configSet.connect(self._on_cfg_set)
        # bit of a hack to take the first item from the guess
        # but should be fine for all use cases this sees
        self._group = (
            group if group is not None else self._core.getOrGuessChannelGroup()[0]
        )
        self._presets = self._core.getAvailableConfigs(self._group)
        self._last_known_preset = ""

    def _on_cfg_set(self, group: str, preset: str) -> None:
        if group == self._group:
            self._last_known_preset = preset

    @property
    def current_channel(self) -> str:
        preset = self._core.getCurrentConfig(self._group)
        if preset == "":
            preset = self._last_known_preset
        else:
            self._last_known_preset = preset
        return preset

    @property
    def current_channel_idx(self) -> int:
        return self.channel_to_idx(self.current_channel)

    def channel_to_idx(self, channel: str):
        return self._presets.index(channel)


class FakeDemoCamera:
    def __init__(
        self,
        img_gen: ImageGenerator = None,
        timing: float = 10,
        core: CMMCorePlus = None,
    ):
        """
        WARNING: Initializing this will override the default demo camera snap function.

        Parameters
        ----------
        img_gen : mda_simulator.ImageGenerator
            If not provided then one with default settings will be created.
            Accesible via the `.img_generator` property
        timing : float, default 10
            The number of real world seconds to wait to update the simulation time
            step.
        core : CMMCorePlus
            If not provided then the current instance will be used
        """
        self._core = core if core else CMMCorePlus.instance()
        self._channel_tracker = ChannelTracker(core=core)
        self._lock = self._core.lock
        self._image = None
        self._img_gen: ImageGenerator = img_gen if img_gen else ImageGenerator(10000)
        self._core.snapImage = self._snapImage
        self._core.getImage = self._getImage
        self._core.getLastImage = self._getLastImage

        self._timing = timing
        self._timer = QTimer()
        self._timer.timeout.connect(self._bump_time)
        if _qt_app_is_running():
            self._timer.start(int(self._timing * 1000))

    @property
    def image_generator(self) -> ImageGenerator:
        return self._img_gen

    @property
    def timing(self) -> float:
        return self._timing

    @timing.setter
    def timing(self, val: float):
        if not isinstance(val, Real) or val <= 0:
            raise ValueError("timing must be a real number > 0")
        self._timing = val
        if self._timer is not None:
            self._timer.setInterval(int(self._timing * 1000))

    def start_timer(self):
        """
        Start the QTimer if not already started, requires a Qt event loop.

        Should only be necessary if this object is created before napari is
        started or if you have paused the timer.
        """
        if self._timer.isActive():
            return
        else:
            self._timer.start(int(self._timing * 1000))

    def pause_timer(self):
        """
        Pause the timer running the simulations
        """
        self._timer.stop()

    def _bump_time(self):
        self._img_gen.increment_time()

    def _snapImage(self) -> None:

        with synchronized(self._lock):
            # self.core
            xy = self._core.getXYPosition()

            c = self._channel_tracker.current_channel_idx
            z = self._core.getPosition()
            exp = self._core.getExposure()
            self._image = self._img_gen.snap_img(xy, c=c, z=z, exposure=exp)

    def _getImage(self, *args, fix=True) -> np.ndarray:
        with synchronized(self._lock):
            if self._image is None:
                raise RuntimeError("Issue snapImage before getImage")
            return self._image

    def _getLastImage(self):
        self._snapImage()
        return self._image
