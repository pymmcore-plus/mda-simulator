from __future__ import annotations

from collections import defaultdict
from functools import lru_cache

import numpy as np
from skimage.color import label2rgb
from skimage.draw import disk

__all__ = [
    "ImageGenerator",
]


class ImageGenerator:
    def __init__(
        self,
        N: int,
        img_shape: tuple[int, int] = (512, 512),
        extent=10,
        radius_loc=25,
        radius_scale=5,
        step_scale: tuple[float, float] = (2.5, 2.5),
        XY_stage_drift: tuple[int, int] = (0, 0),
    ):
        self._rng = np.random.default_rng()
        self._N = N
        self._ids = np.arange(N)
        self._radii = self._rng.normal(radius_loc, radius_scale, N)
        self._colors = self._rng.random((N, 3))
        self._shape = np.array(img_shape)
        X = self._rng.uniform(-self._shape[0] * extent, self._shape[0] * extent, (N, 1))
        Y = self._rng.uniform(-self._shape[1] * extent, self._shape[1] * extent, (N, 1))
        self._pos = np.hstack((X, Y))
        self._step_scale = np.asarray(step_scale)
        self._stage_drift = np.array(XY_stage_drift)
        # A is per channel
        self._A: dict[int, np.ndarray] = defaultdict(
            lambda: np.abs(self._rng.normal(1024, 256))
        )
        # sigma dict is per cell/per channel
        self._sigma: dict[int, np.ndarray] = defaultdict(
            lambda: 1
            + np.abs(self._rng.normal(radius_loc / 10, radius_scale / 10, size=self._N))
        )

    @property
    def img_shape(self) -> np.ndarray:
        return self._shape

    def snap_img(self, xy: tuple[float, float], c: int = 0, z: float = 0, exposure=1):
        return self._snap_img(tuple(xy), c, z, exposure)

    @lru_cache(256)
    def _snap_img(self, xy: tuple[float, float], c: int = 0, z: float = 0, exposure=1):
        # print('here')
        x_idx = (self._pos[:, 0] < xy[0] + self._shape[0] // 2) & (
            self._pos[:, 0] > xy[0] - self._shape[0] // 2
        )
        y_idx = (self._pos[:, 1] < xy[1] + self._shape[1] // 2) & (
            self._pos[:, 1] > xy[1] - self._shape[1] // 2
        )
        idx = x_idx & y_idx

        coords = self._pos[idx] + (self._shape / 2 - np.asarray(xy))[None, :]
        radii = self._radii[idx]
        inter = radii**2 - z**2
        inter[inter < 0] = 0
        radii = np.sqrt(inter)
        sigmas = self._sigma[c][idx]
        A = self._A[c]
        ids = self._ids[idx]

        out = np.zeros(self._shape, dtype=np.uint16)

        for pos, r, id_, sigma in zip(coords, radii, ids, sigmas):

            pixels = disk(pos, r, shape=self._shape)
            if c > 0:
                dists = np.sqrt((pixels[0] - pos[0]) ** 2 + (pixels[1] - pos[1]) ** 2)
                intensity = exposure * A * np.exp(-dists / (2 * sigma**2))
            else:
                intensity = id_
            out[pixels] = intensity
        return out

    def image2rgb(self, img):
        """
        Convert a grayscale image from this generator to RGB for easy viewing
        Parameters
        ----------
        img : (M, M) of int
        Returns
        -------
        (M, M, 3) of float
        """
        # label2rgb doesn't do this indexing, it just works from the lowest number
        # as the first color in the list. So do the indexing for it.
        idx = np.floor(np.unique(img)).astype(int)
        return label2rgb(img, colors=self._colors[idx])

    def increment_time(self, delta_t=1):
        """increment the simulation time by delta_t time units."""
        # clear the cache as the image will have changed
        self._snap_img.cache_clear()

        self._pos += self._rng.normal(
            scale=self._step_scale * delta_t, size=(self._N, 2)
        ) + np.array(self._stage_drift)
