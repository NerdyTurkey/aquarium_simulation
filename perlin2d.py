import pygame as pg
import numpy as np
import time


def interpolant(t):
    return t*t*t*(t*(t*6 - 15) + 10)


def generate_perlin_noise_2d(
        shape, res, tileable=(False, False), interpolant=interpolant
):
    """Generate a 2D numpy array of perlin noise.
    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multple of res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints). Note shape must be a multiple of
            res.
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).
    Returns:
        A numpy array of shape shape with the generated noise.
    Raises:
        ValueError: If shape is not a multiple of res.
    """
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]]\
             .transpose(1, 2, 0) % 1
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    if tileable[0]:
        gradients[-1,:] = gradients[0,:]
    if tileable[1]:
        gradients[:,-1] = gradients[:,0]
    gradients = gradients.repeat(d[0], 0).repeat(d[1], 1)
    g00 = gradients[    :-d[0],    :-d[1]]
    g10 = gradients[d[0]:     ,    :-d[1]]
    g01 = gradients[    :-d[0],d[1]:     ]
    g11 = gradients[d[0]:     ,d[1]:     ]
    # Ramps
    n00 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]  )) * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]  )) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = interpolant(grid)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    result = 128*(1+ np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1))
    return result.astype("uint8")  # int 0-255

#
# def generate_perlin_noise_2d(shape, res):
#     """ shape must be a multiple of res """
#
#     def f(t):
#         return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3
#
#     delta = (res[0] / shape[0], res[1] / shape[1])
#     d = (shape[0] // res[0], shape[1] // res[1])
#     grid = np.mgrid[0 : res[0] : delta[0], 0 : res[1] : delta[1]].transpose(1, 2, 0) % 1
#     # Gradients
#     angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
#     gradients = np.dstack((np.cos(angles), np.sin(angles)))
#     g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
#     g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
#     g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
#     g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
#     # Ramps
#     n00 = np.sum(grid * g00, 2)
#     n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
#     n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
#     n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
#     # Interpolation
#     t = f(grid)
#     n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
#     n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
#     #  float 0 - 255
#     result = 128 * (1 + np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1))
#     return result.astype("uint8")  # int 0-255
#

def main():
    w, h = 1200, 800
    pg.init()
    screen = pg.display.set_mode((w, h))
    np.random.seed(0)
    noise = generate_perlin_noise_2d((w, h), (8, 8), tileable=(True, False))
    surf = pg.Surface((w, h), pg.SRCALPHA)
    surf.fill((0, 0, 250))
    alphas = pg.surfarray.pixels_alpha(surf)
    alphas[:] = noise[:]
    # surf is locked (i.e. can't blit or save) until alphas is deleted
    del alphas
    pg.image.save(surf, "underseaT2.png")
    screen.blit(surf, (0, 0))
    pg.display.flip()
    pg.time.delay(4000)
    pg.quit()


if __name__ == "__main__":
    main()
