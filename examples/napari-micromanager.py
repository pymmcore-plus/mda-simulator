"""
Example of using with Napari-Micromanager

pip install napari-micromanager

After you run the MDA make sure to reset the histogram for the non-BF channels,
otherwise you will be unable to see the spatial variation.

"""
from pathlib import Path

import napari
from pymmcore_plus import CMMCorePlus
from useq import MDASequence

from mda_simulator import ImageGenerator
from mda_simulator.mmcore import FakeDemoCamera

v = napari.Viewer()
dw, main_window = v.window.add_plugin_dock_widget("napari-micromanager")

core = CMMCorePlus.instance()
core.loadSystemConfiguration(Path(__file__).parent / "config.cfg")

gen = ImageGenerator(N=4000)


# Create an object that will modify the `snap` method of the CMMCorePlus
# instance to return images from our ImageGenerator
fake_cam = FakeDemoCamera(
    gen,
    timing=10,  # how many real world seconds to wait to step the ImageGenerator time
    core=core,
)

mda = MDASequence(
    channels=[
        "BF",
        {"config": "DAPI", "exposure": 1},
        {"config": "FITC", "exposure": 10},
    ],
    time_plan={"interval": 30, "loops": 4},
    z_plan={"range": 50, "step": 5},
    axis_order="tpcz",
    stage_positions=[(0, 1, 1), (512, 128, 0)],
)

core.run_mda(mda)
v.show(block=True)
