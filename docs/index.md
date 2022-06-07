
# mda-simulator's Documentation

mda simulator provides a convenient way to generate images for fake microscopy time series (Time, Position, Channel, Slice) useful when developing microscope control software or for tests of downstream analysis libraries.

It maintains the position of many cells (rendered as spheres) and moves them according a random walk whenever you ask it to step forward in time. Each cell has a different size and slightly different responses to different channels. There is also spatial variation within each cell for the fluorescent channels.

![Gif of usage in napari](_static/example-napari.apng)


## Install
```bash
pip install mda-simulator
```



```{toctree}
:maxdepth: 2

API <api/mda_simulator>
contributing
```

```{toctree}
:caption: Examples
:maxdepth: 1

examples/standalone-usage.ipynb
examples/napari-micromanager.ipynb
```
