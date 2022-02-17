import FESTIM as F

mesh = F.MeshFromXDMF("fe_mesh/mesh_domains.xdmf", "fe_mesh/mesh_boundaries.xdmf")

id_flibe = 6
id_steel = 7

id_top_flibe = 8
id_gas_steel_interface = 9

materials = F.Materials([
    F.Material(id_flibe, 1, 0),  # flibe
    F.Material(id_steel, 1, 0),  # steel
])

sources = [
    F.Source(1e10, id_flibe, "solute")
]

boundary_conditions = [
    F.DirichletBC(id_top_flibe, 0),
    F.DirichletBC(id_gas_steel_interface, 0),
]

T = F.Temperature(600)

settings = F.Settings(1e10, 1e-10, transient=False)

exports = F.Exports([
    F.XDMFExport("solute", "hydrogen_concentration", "results")
])

sim = F.Simulation(
    mesh=mesh,
    materials=materials,
    sources=sources,
    boundary_conditions=boundary_conditions,
    temperature=T,
    settings=settings,
    exports=exports
    )

sim.initialise()
sim.run()
