import openmc
from scipy import interpolate
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib import ticker
import matplotx
import numpy as np
import scipy.ndimage as ndimage


def reshape_values_to_mesh_shape(tally, values):
    mesh_filter = tally.find_filter(filter_type=openmc.MeshFilter)
    # shape = mesh_filter.mesh.dimension.tolist()
    shape = [
        len(mesh_filter.mesh.r_grid) - 1,
        len(mesh_filter.mesh.phi_grid) - 1,
        len(mesh_filter.mesh.z_grid) - 1,
    ]
    # 2d mesh has a shape in the form [1, 400, 400]
    if 1 in shape:
        shape.remove(1)
    return values.reshape(shape[::-1])

def get_tally_extent(tally):

    for filter in tally.filters:
        if isinstance(filter, openmc.MeshFilter):
            mesh_filter = filter

    extent_x = (
        min(mesh_filter.mesh.r_grid),
        max(mesh_filter.mesh.r_grid),
    )
    extent_y = (
        min(mesh_filter.mesh.phi_grid),
        max(mesh_filter.mesh.phi_grid),
    )
    extent_z = (
        min(mesh_filter.mesh.z_grid),
        max(mesh_filter.mesh.z_grid),
    )
    shape = [
        len(mesh_filter.mesh.r_grid) - 1,
        len(mesh_filter.mesh.phi_grid) - 1,
        len(mesh_filter.mesh.z_grid) - 1,
    ]
    if 1 in shape:
        print("2d mesh tally")
        index_of_1d = shape.index(1)
        print("index", index_of_1d)
        if index_of_1d == 0:
            (left, right) = extent_y
            (bottom, top) = extent_z
        if index_of_1d == 1:
            (left, right) = extent_x
            (bottom, top) = extent_z
        if index_of_1d == 2:
            (left, right) = extent_x
            (bottom, top) = extent_y
        return (left, right, bottom, top)
    return None


def interpolate_tally(tally, sigma=3.0):
    mesh = tally.find_filter(filter_type=openmc.MeshFilter).mesh

    data = tally.get_pandas_dataframe()
    mean = np.array(data["mean"])
    
    # convert tally
    mean *= source_strength
    volumes = mesh.calc_mesh_volumes().T.flatten()
    mean = mean/volumes

    mean = reshape_values_to_mesh_shape(tally, mean)

    # # Interpolate data

    # get centers of row and column
    centers_x = (mesh.r_grid[1:] + mesh.r_grid[:-1]) / 2
    centers_y = (mesh.z_grid[1:] + mesh.z_grid[:-1]) / 2

    mean = ndimage.gaussian_filter(mean, sigma=sigma, order=0)

    # too heavy for big arrays
    # https://stackoverflow.com/questions/63668864/scipy-interpolate-interp2d-do-i-really-have-too-many-data-points?rq=1
    # xx, yy = np.meshgrid(centers_x, centers_y)
    f = interpolate.interp2d(centers_x, centers_y, mean, kind='linear')
    return f


source_strength = 1e10/4  # n/s
statepoint_file = "statepoint.4.h5"

# loads up the statepoint file with simulation results
statepoint = openmc.StatePoint(filepath=statepoint_file)
t_prod_cyl = statepoint.get_tally(name="(n,Xt)_cylindrical")

mean = np.array(t_prod_cyl.get_pandas_dataframe()["mean"])
mesh = t_prod_cyl.find_filter(filter_type=openmc.MeshFilter).mesh
volumes = mesh.calc_mesh_volumes().T.flatten()

mean = mean/volumes*source_strength  # convert tally

mean = reshape_values_to_mesh_shape(t_prod_cyl, mean)

with plt.style.context(matplotx.styles.dufte):
    fig, axs = plt.subplots(1, 2, sharey=True, sharex=True, figsize=(6.4, 5.4))

    # plot real data
    plt.sca(axs[0])
    plt.gca().set_title("Real")
    matplotx.ylabel_top("Z [cm]")
    plt.xlabel("X [cm]")
    image_map = plt.imshow(mean, extent=get_tally_extent(t_prod_cyl), origin="lower", zorder=1, cmap='Purples', norm=LogNorm(vmin=1e3))
    plt.scatter(0.1, 66)

    # plot interpolated data
    plt.sca(axs[1])
    plt.gca().set_title("Interpolated + Smoothed", size=12)
    plt.xlabel("X [cm]")
    x_new = np.linspace(0, 50, 600)
    y_new = np.linspace(0, 110, 600)
    xx, yy = np.meshgrid(x_new, y_new)
    z = interpolate_tally(t_prod_cyl, sigma=3)(x_new, y_new)
    z.reshape(y_new.size, x_new.size)
    levels = np.logspace(3, np.log10(mean.max()), 100)
    cs = plt.contourf(xx, yy, z, levels=levels, cmap='Purples', norm=LogNorm(vmin=1e3))
    levels2 = np.logspace(4, np.log10(mean.max()), 6, endpoint=False)
    plt.contour(xx, yy, z, levels=levels2, colors="white", alpha=0.3)
    plt.scatter(0.1, 66)
    plt.colorbar(image_map, ax=axs.ravel().tolist(), label="T production rate (T/m3/s)")
    plt.gca().set_aspect('equal')

    # plt.tight_layout()
    plt.savefig('real_vs_interpolated.png')
