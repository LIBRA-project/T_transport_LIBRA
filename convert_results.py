import openmc
from regular_mesh_plotter import plot_regular_mesh_tally_with_geometry
from openmc_mesh_tally_to_vtk import write_mesh_tally_to_vtk

# can be used to scale the color scale
from matplotlib.colors import LogNorm


statepoint_file = "statepoint.4.h5"

# loads up the statepoint file with simulation results
statepoint = openmc.StatePoint(filepath=statepoint_file)

t_prod = statepoint.get_tally(name="(n,Xt)_on_2D_mesh_xz")
heating = statepoint.get_tally(name="heating_on_2D_mesh_yz")
tbr = statepoint.get_tally(name="TBR")

print("The TBR is {}".format(tbr.mean))
print("The TBR std dev is {}".format(tbr.std_dev))

# LIBRA --> fluence 1e10 n/s
source_strength = 1e10  # n/s
# TODO divide by 4?


plot_regular_mesh_tally_with_geometry(
    tally=t_prod,
    dagmc_file_or_trimesh_object="dagmc_not_merged.h5m",
    plane_origin=(0, 0, 0),
    plane_normal=[0, 1, 0],
    rotate_geometry=90,
    source_strength=source_strength,
    scale=LogNorm(vmin=1e1),
    label="Tritium generation (T/m3/s)",
    filename="t_production.png",
)


plot_regular_mesh_tally_with_geometry(
    tally=heating,
    dagmc_file_or_trimesh_object="dagmc_not_merged.h5m",
    plane_origin=(0, 0, 0),
    plane_normal=[0, 1, 0],
    rotate_geometry=90,
    source_strength=source_strength,
    required_units="W per m**3",
    scale=LogNorm(),
    label="Nuclear heating (W/m3/s)",
    filename="heating.png",
)


write_mesh_tally_to_vtk(
    tally=t_prod,
    filename = "t_production.vtk",
)
write_mesh_tally_to_vtk(
    tally=heating,
    filename = "heating.vtk",
)
