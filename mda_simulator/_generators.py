from __future__ import annotations

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
        step_scale: tuple[int, int] = (5, 5),
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
        self._step_scale = step_scale
        self._stage_drift = np.array(XY_stage_drift)

    def snap_img(self, image_loc: tuple[float, float], z: float = 0, as_rgb=False):
        x_idx = (self._pos[:, 0] < image_loc[0] + self._shape[0] // 2) & (
            self._pos[:, 0] > image_loc[0] - self._shape[0] // 2
        )
        y_idx = (self._pos[:, 1] < image_loc[1] + self._shape[1] // 2) & (
            self._pos[:, 1] > image_loc[1] - self._shape[1] // 2
        )
        idx = x_idx & y_idx

        coords = self._pos[idx] + (self._shape / 2 - np.asarray(image_loc))[None, :]
        radii = self._radii[idx]
        inter = radii ** 2 - z ** 2
        inter[inter < 0] = 0
        radii = np.sqrt(inter)
        ids = self._ids[idx]

        out = np.zeros(self._shape, dtype=np.uint16)
        for pos, r, id_ in zip(coords, radii, ids):
            # r = np.sqrt(inter)
            out[disk(pos, r, shape=self._shape)] = id_

        if as_rgb:
            return label2rgb(out, colors=self._colors[idx])
            # return self.image2rgb(out)
        else:
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

    def step_positions(self, delta_t=1):
        self._pos += self._rng.normal(
            scale=self._step_scale * delta_t, size=(self._N, 2)
        ) + np.array(self._stage_drift)
