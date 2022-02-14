from stl_to_h5m import stl_to_h5m


stl_filenames = ['inner_tank_wall.stl', 'outer_tank_wall.stl', 'lead.stl', 'flibe.stl']
compentent_names = ['inner_tank_wall', 'outer_tank_wall', 'lead', 'flibe']

stl_to_h5m(
    files_with_tags=[(stl_filename, name) for name, stl_filename in zip(compentent_names, stl_filenames)],
    h5m_filename='dagmc_not_merged.h5m',
)
