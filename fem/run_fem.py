from sources.interpolate_sources import t_source
from custom_source import InterpolatedSource
import fenics as f

import FESTIM as F

mesh = F.MeshFromXDMF("fe_mesh/mesh_domains_2D.xdmf", "fe_mesh/mesh_boundaries_2D.xdmf", type="cylindrical")

id_flibe = 6
id_steel = 7

id_top_flibe = 8
id_gas_steel_interface = 9

avogadro = 6.022e23  # mol-1

KSsteel = 3e-2*avogadro
KHflibe = 5e-4*avogadro  # see Figure 1 https://www.osti.gov/biblio/1777267-tritium-transport-phenomena-molten-salt-reactors

materials = F.Materials([
    F.Material(id_flibe, D_0=1e-8, E_D=0, S_0=KHflibe, E_S=0, solubility_law="henry"),  # flibe
    F.Material(id_steel, D_0=1e-8, E_D=0, S_0=KSsteel, E_S=0, solubility_law="sieverts"),  # steel
])


tritium_source = InterpolatedSource(t_source, id_flibe, "solute")
sources = [
    tritium_source
]

boundary_conditions = [
    F.DirichletBC(id_top_flibe, 0),
    F.DirichletBC(id_gas_steel_interface, 0),
]

T = F.Temperature(600)

settings = F.Settings(1e-3, 1e-10, transient=False, chemical_pot=False, maximum_iterations=100)

xdmf_export = F.XDMFExport("solute", "hydrogen_concentration_continuous", "results")
exports = F.Exports([
    xdmf_export
])

# STEP 1 continuity of concentration
print('STEP 1')
sim = F.Simulation(
    mesh=mesh,
    materials=materials,
    sources=sources,
    boundary_conditions=boundary_conditions,
    temperature=T,
    settings=settings,
    exports=exports,
    log_level=20
    )

sim.initialise()

sim.run()

# STEP 2
print('STEP 2')
old_c = sim.mobile.solution

settings.chemical_pot = True
xdmf_export.append = False
xdmf_export.label = "hydrogen_concentration_discontinuity"
xdmf_export.define_xdmf_file()

sim2 = F.Simulation(
    mesh=mesh,
    materials=materials,
    sources=sources,
    boundary_conditions=boundary_conditions,
    temperature=T,
    settings=settings,
    exports=exports,
    log_level=20
    )

sim2.initialise()

# use old solution as initial guess
sim2.mobile.solution.assign(f.project(old_c*1e-14, sim2.h_transport_problem.V))

sim2.run()
