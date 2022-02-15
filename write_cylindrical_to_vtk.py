import numpy as np
import vtk
import math
import openmc

import openmc_tally_unit_converter as otuc


def get_mesh_from_tally(tally: openmc.Tally):
    """Extracts the mesh from a tally
    Args: the tally to extract the mesh from. Should have a MeshFilter as one
        of the filters.
    Returns: an openmc.RegularMesh object
    """

    if tally.contains_filter(openmc.MeshFilter):
        mesh_filter = tally.find_filter(filter_type=openmc.MeshFilter)
    else:
        msg = "Tally does not contain a MeshFilter"
        raise ValueError(msg)

    mesh = mesh_filter.mesh

    return mesh


def replace_nans_with_zeros(list_of_numbers: list):
    """Replaces any NaN present in a list with 0.
    Args: a list of floats and which optionally contains NaNs
    Returns: a list of floats
    """

    for counter, i in enumerate(list_of_numbers):
        if math.isnan(i):
            list_of_numbers[counter] = 0.0
    return list_of_numbers


def find_coords_of_mesh(mesh: openmc.CylindricalMesh):

    xs = mesh.r_grid
    ys = mesh.phi_grid
    zs = mesh.z_grid

    return xs, ys, zs


def write_vtk(
    xs,
    ys,
    zs,
    tally_data,
    filename: str,
    label: str = "made with openmc_mesh_tally_to_vtk",
    error_data=None,
):

    vtk_box = vtk.vtkRectilinearGrid()

    vtk_box.SetDimensions(len(xs), len(ys), len(zs))

    vtk_x_array = vtk.vtkDoubleArray()
    vtk_x_array.SetName("x-coords")
    vtk_x_array.SetArray(xs, len(xs), True)
    vtk_box.SetXCoordinates(vtk_x_array)

    vtk_y_array = vtk.vtkDoubleArray()
    vtk_y_array.SetName("y-coords")
    vtk_y_array.SetArray(ys, len(ys), True)
    vtk_box.SetYCoordinates(vtk_y_array)

    vtk_z_array = vtk.vtkDoubleArray()
    vtk_z_array.SetName("z-coords")
    vtk_z_array.SetArray(zs, len(zs), True)
    vtk_box.SetZCoordinates(vtk_z_array)

    tally = np.array(tally_data)
    tally_data = vtk.vtkDoubleArray()
    tally_data.SetName(label)
    print("tally.size", tally.size)
    print("tally", tally)
    tally_data.SetArray(tally, tally.size, True)

    if error_data is not None:
        error = np.array(error_data)
        error_data = vtk.vtkDoubleArray()
        error_data.SetName("error_tag")
        error_data.SetArray(error, error.size, True)

    vtk_box.GetCellData().AddArray(tally_data)
    if error_data is not None:
        vtk_box.GetCellData().AddArray(error_data)

    writer = vtk.vtkRectilinearGridWriter()

    writer.SetFileName(filename)

    writer.SetInputData(vtk_box)

    print("Writing %s" % filename)

    writer.Write()

    return filename


def write_mesh_tally_to_vtk(
    tally,
    filename: str = "vtk_file_from_openmc_mesh.vtk",
    required_units: str = None,
    source_strength: float = None,
    include_std_dev: bool = True,
):
    """Writes a regular mesh tally to a VTK file. If required units are specified
    then the openmc_tally_unit_converter package will attempt to convert the tally
    values into the required units.
    Args:
        tally:
        filename: the filename of the vtk produced.
        required_units: units to convert the tally results into.
        source_strength: particles per second or particles per pulse which can
            also be provided to assist with unit conversion.
        include_std_dev: controls whether the std dev of the tally is written
            to the vtk file. Assuming std dev data is present then it will be
            written to the vtk file by default. This option allows std dev to
            not be written to the vtk file which can help reduce the file size
            of the vtk file.
    Returns: The filename of the vtk file produced
    """

    if required_units is None:
        tally_data = tally.mean[:, 0, 0]
        tally_data = tally_data.tolist()
        tally_data = replace_nans_with_zeros(tally_data)
        if include_std_dev:
            error_data = tally.std_dev[:, 0, 0]
            # if std_dev is all nan values then batches was 1 and there is no need
            # to add this to the vtk
            if np.isnan(error_data).all():
                error_data = None
            else:
                error_data = error_data.tolist()
                error_data = replace_nans_with_zeros(error_data)
        else:
            error_data = None
    else:
        tally_data, error_data = otuc.process_tally(
            tally, required_units=required_units, source_strength=source_strength
        )

    mesh = get_mesh_from_tally(tally)

    xs, ys, zs = find_coords_of_mesh(mesh)

    output_filename = write_vtk(
        xs=xs,
        ys=ys,
        zs=zs,
        tally_data=tally_data,
        error_data=error_data,
        filename=filename,
        label=tally.name,
    )

    return output_filename

