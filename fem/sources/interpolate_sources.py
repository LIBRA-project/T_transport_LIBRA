import os

from scipy import interpolate, ndimage
import numpy as np


def interpolate_source(xfile, yfile, meanfile, sigma=3):

    centers_x = np.genfromtxt(xfile)
    centers_y = np.genfromtxt(yfile)
    mean = np.genfromtxt(meanfile)

    mean = ndimage.gaussian_filter(mean, sigma=sigma, order=0)

    # too heavy for big arrays
    # https://stackoverflow.com/questions/63668864/scipy-interpolate-interp2d-do-i-really-have-too-many-data-points?rq=1
    # xx, yy = np.meshgrid(centers_x, centers_y)
    f = interpolate.interp2d(centers_x, centers_y, mean, kind='linear')
    return f


script_dir = os.path.dirname(__file__)

t_source = interpolate_source(
    os.path.join(script_dir, "t_production/x.txt"),
    os.path.join(script_dir, "t_production/y.txt"),
    os.path.join(script_dir, "t_production/mean.txt")
)
