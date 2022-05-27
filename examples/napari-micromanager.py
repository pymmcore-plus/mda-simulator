"""
Example of using with Napari-Micromanager

For installing everything:

pip install napari-micromanager
pip install git+https://github.com/ianhi/pymmcore-MDA-engines


After you run the MDA make sure to reset the histogram for the non-BF channels,
otherwise you will be unable to see the spatial variation.

"""
from pathlib import Path

import napari
from pymmcore_mda_engines import DevEngine
from pymmcore_plus import CMMCorePlus
from useq import MDASequence

from mda_simulator import ImageGenerator

v = napari.Viewer()
dw, main_window = v.window.add_plugin_dock_widget("napari-micromanager")

core = CMMCorePlus.instance()
core.loadSystemConfiguration(Path(__file__).parent / "config.cfg")

gen = ImageGenerator(4000)

# engine that uses an ImageGenerator by default
engine = DevEngine(image_generator=gen)
core.register_mda_engine(engine)

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
