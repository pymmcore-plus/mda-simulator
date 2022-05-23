# isort: skip_file
# idk why but htis order of imports matters
from mda_simulator import ImageGenerator
import matplotlib.pyplot as plt

# without hte above order hyperslicer doesn't work

import numpy as np
from mpl_interactions import hyperslicer


img_gen = ImageGenerator(10000)


T = 45
P = 3

image_locations = [
    (-512, 0),
    (0, 0),
    (0, 512),
]

out = np.zeros([T, P, 512, 512])
out_rgb = np.zeros([T, P, 512, 512, 3])

for t in range(T):
    for p in range(P):
        out[t, p] = img_gen.snap_img(image_locations[p])
        out_rgb[t, p] = img_gen.snap_img(image_locations[p], as_rgb=True)
    img_gen.step_positions()
plt.figure()
hyperslicer(out_rgb, is_color_image=True)
plt.show()
