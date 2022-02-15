import openmc
import openmc_dagmc_wrapper as odw
import openmc_plasma_source as ops
import neutronics_material_maker as nmm
import math
import numpy as np

my_h5m_filename = "dagmc_not_merged.h5m"

# materials
material_tag_to_material_dict = {
    "lead": "Lead",
    "flibe": nmm.Material.from_library(name="FLiBe", enrichment=90, temperature=650+273.15, pressure=1e5, temperature_to_neutronics_code=False),
    "inner_tank_wall": "SS_316L_N_IG",
    "outer_tank_wall": "SS_316L_N_IG",
}

materials = odw.Materials(
    h5m_filename=my_h5m_filename,
    correspondence_dict=material_tag_to_material_dict,
)

# Geometry
geometry = odw.Geometry(
    h5m_filename=my_h5m_filename,
    reflective_angles=[0, math.pi/2]
    )
bounding_box = geometry.corners()

# Tallies
t_prod = odw.MeshTally2D(tally_type="(n,Xt)", plane="xz", bounding_box=bounding_box)
t_prod.name = "(n,Xt)_regular"

t_prod_cyl = openmc.Tally(name="(n,Xt)_cylindrical")
t_prod_cyl.scores = ["(n,Xt)"]
cylindrical_mesh = openmc.CylindricalMesh()
cylindrical_mesh.r_grid = np.linspace(bounding_box[0][0], bounding_box[1][0], num=400)
cylindrical_mesh.phi_grid = [0, math.pi/2]
cylindrical_mesh.z_grid = np.linspace(bounding_box[0][2], bounding_box[1][2], num=400)
t_prod_cyl.filters.append(openmc.MeshFilter(cylindrical_mesh))

heating = odw.MeshTally2D(tally_type="heating", plane="yz", bounding_box=bounding_box)
tbr = odw.CellTally(tally_type="TBR")

tallies = openmc.Tallies([t_prod, t_prod_cyl, heating, tbr])

# settings
settings = odw.FusionSettings()
settings.batches = 4
settings.particles = 1000
settings.source = ops.FusionPointSource(fuel="DT", coordinate=(5, 5, 50))


my_model = openmc.Model(
    materials=materials, geometry=geometry, settings=settings, tallies=tallies
)

# Run
statepoint_file = my_model.run()

print(f'neutronics results are saved in {statepoint_file}')
