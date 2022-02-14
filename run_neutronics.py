import openmc
import openmc_dagmc_wrapper as odw
import openmc_plasma_source as ops
import neutronics_material_maker as nmm
import math

# could set to dagmc.h5m if the imprinted and merged geometry is preferred
my_h5m_filename = "dagmc_not_merged.h5m"

# this links the material tags in the dagmc h5m file with materials.
# these materials are input as strings so they will be looked up in the
# neutronics material maker package
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

geometry = odw.Geometry(
    h5m_filename=my_h5m_filename,
    reflective_angles=[0, math.pi/2]
    )
bounding_box = geometry.corners()


t_prod = odw.MeshTally2D(tally_type="(n,Xt)", plane="xz", bounding_box=bounding_box)
heating = odw.MeshTally2D(tally_type="heating", plane="yz", bounding_box=bounding_box)
tbr = odw.CellTally(tally_type="TBR")

tallies = openmc.Tallies([t_prod, heating, tbr])

settings = odw.FusionSettings()
settings.batches = 4
settings.particles = 1000
settings.source = ops.FusionPointSource(fuel="DT", coordinate=(5, 5, 50))


my_model = openmc.Model(
    materials=materials, geometry=geometry, settings=settings, tallies=tallies
)

# starts the simulation
statepoint_file = my_model.run()

print(f'neutronics results are saved in {statepoint_file}')
