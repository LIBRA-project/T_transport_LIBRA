from sources.interpolate_sources import t_source
from custom_source import InterpolatedSource
import fenics as f

import FESTIM as F

mesh = F.MeshFromXDMF("fe_mesh/mesh_domains.xdmf", "fe_mesh/mesh_boundaries.xdmf")

id_flibe = 6
id_steel = 7

id_top_flibe = 8
id_gas_steel_interface = 9

materials = F.Materials([
    F.Material(id_flibe, 1, 0, 2, 0, thermal_cond=1, solubility_law="henry"),  # flibe
    F.Material(id_steel, 1, 0, 1, 0, thermal_cond=1, solubility_law="henry"),  # steel
])


tritium_source = InterpolatedSource(t_source, id_flibe, "solute")
sources = [
    # F.Source(1e10, id_flibe, "solute")
    tritium_source
]

boundary_conditions = [
    F.DirichletBC(id_top_flibe, 0),
    F.DirichletBC(id_gas_steel_interface, 0),
]

T = F.Temperature(600)

settings = F.Settings(1e3, 1e-10, transient=False, chemical_pot=True, maximum_iterations=50)

exports = F.Exports([
    F.XDMFExport("solute", "hydrogen_concentration", "results")
])

# need an initial guess to make the solver converge quicker
initial_conditions = [
    F.InitialCondition(value=0.5e3, field=0),
]

sim = F.Simulation(
    mesh=mesh,
    materials=materials,
    sources=sources,
    boundary_conditions=boundary_conditions,
    initial_conditions=initial_conditions,
    temperature=T,
    settings=settings,
    exports=exports,
    log_level=20
    )

sim.initialise()

# tritium_source.value = f.project(tritium_source.value, sim.h_transport_problem.V_CG1)
sim.run()
