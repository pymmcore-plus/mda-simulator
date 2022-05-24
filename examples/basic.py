# isort: skip_file
# idk why but htis order of imports matters
from mda_simulator import ImageGenerator

# import matplotlib.pyplot as plt

# without hte above order hyperslicer doesn't work

import numpy as np

# from mpl_interactions import hyperslicer


img_gen = ImageGenerator(10000)


T = 5
P = 1
Z = 10

image_locations = [
    (-512, 0),
    (0, 0),
    (0, 512),
]

out = np.zeros([T, P, Z, 512, 512])
out_rgb = np.zeros([T, P, Z, 512, 512, 3])

for t in range(T):
    for p in range(P):
        for zi, z in enumerate(np.linspace(-30, 30, Z)):
            out[t, p, zi] = img_gen.snap_img(image_locations[p], z=z)
            # out_rgb[t, p, zi] = img_gen.snap_img(image_locations[p], z=z, as_rgb=True)
    img_gen.step_positions()
# plt.figure()
# hyperslicer(out_rgb, is_color_image=True)
# hyperslicer(out_rgb, is_color_image=True)
# plt.show()
