import numpy as np

color = (255, 0, 238, 100)
r = (mask * color[0]).reshape((w * h))
g = (mask * color[1]).reshape((w * h))
b = (mask * color[2]).reshape((w * h))
a = (mask * color[3]).reshape((w * h))

rgba = np.dstack((r, g, b, a)).reshape((w, h, 4))
transposed = np.transpose(rgba, axes=[1, 0, 2])
