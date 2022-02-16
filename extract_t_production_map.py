import openmc
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np


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
    return values.reshape(shape)

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
            return extent_y + extent_z
        if index_of_1d == 1:
            return extent_x + extent_z
        if index_of_1d == 2:
            return extent_x + extent_y
    return None

source_strength = 1e10/4  # n/s
statepoint_file = "statepoint.4.h5"

# loads up the statepoint file with simulation results
statepoint = openmc.StatePoint(filepath=statepoint_file)

t_prod_cyl = statepoint.get_tally(name="(n,Xt)_cylindrical")
data = t_prod_cyl.get_pandas_dataframe()
mean = np.array(data["mean"])*source_strength
mean = reshape_values_to_mesh_shape(t_prod_cyl, mean)

# # Interpolate data

mesh = t_prod_cyl.find_filter(filter_type=openmc.MeshFilter).mesh

# get centers of row and column
centers_x = (mesh.r_grid[1:] + mesh.r_grid[:-1]) / 2
centers_y = (mesh.z_grid[1:] + mesh.z_grid[:-1]) / 2

# too heavy for big arrays
# https://stackoverflow.com/questions/63668864/scipy-interpolate-interp2d-do-i-really-have-too-many-data-points?rq=1
# xx, yy = np.meshgrid(centers_x, centers_y)
f = interpolate.interp2d(centers_x, centers_y, mean, kind='linear')

fig, axs = plt.subplots(1, 2)

# plot real data
plt.sca(axs[0])
image_map = plt.imshow(mean, extent=get_tally_extent(t_prod_cyl), origin="lower", cmap="Purples")

# plot interpolated data
plt.sca(axs[1])
x_new = mesh.r_grid
y_new = mesh.z_grid
z = f(x_new, y_new)
plt.contourf(x_new, y_new, z, levels=np.linspace(0, mean.max(), 100), cmap='Purples')
plt.colorbar(image_map, ax=axs.ravel().tolist())
plt.gca().set_aspect('equal')
plt.savefig('real_vs_interpolated.png')
