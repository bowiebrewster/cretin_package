import generator_object
import write_run_plot
import serial_sim_tools
import new_plt_file
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from importlib import reload
for obj in [generator_object, write_run_plot, serial_sim_tools, new_plt_file]:
    reload(obj)


def sim3(var2):

    gen = generator_object.User_input()
    n_atom = 50
    rho, T_ev = 15, var2
    z = 12
    N0, N1 = 1, 501  # We are operating in 1d wih 40 nodes
    Rmin, Rmax = 0, 0.01
    p2 = 1.e-9

    gen.materials_atom(index=1, quantum_n_max=3, element="sn")
    gen.materials_region(nodes=[N0, N1], elec_temp=T_ev, qstart=True)

    gen.materials_region_material(rho, n_atom, z, z**2)

    gen.geometry(type='slab')
    gen.geometry_nodes(coordinate="r", scaling_type="geom", nodes=[
                       N0, N1], nodes_range=[Rmin, Rmax], drmin=1.e-6, slope=-1)

    gen.sources_laser(index=1, laser_wavelength=1, option_1='value',
                      option_2='history', id_value=1, multiplier=1,)
    gen.sources_lasray(entrance_position=10, entrance_direction_mu=1,
                       entrance_direction_phi=0, fractional_power=1, res_frac=.5)

    gen.sources_history(id=1, value_multiplier=1e18,
                        time_multiplier=1., pulse_type='gaussian', p1=5*p2, p2=p2)

    gen.popular_switches(timestep_between_snapshot=500,
                         temparture_calc_heating_rates=[
                             'temp calc = time dependant', 'heating rates = electronic'],
                         raytrace=True,
                         include_degeneracy='no degeneracy',
                         continuum_transfer_evolves_temp=True)

    gen.other_switches(resonant_absorption_fraction='constant value for each ray from lasray',
                       subcycle_maximum=1000,
                       do_kinetics_zone_centered=True,
                       population_calculation='time dependent diffusion',
                       control_calc_thermal_conduct='include thermal conduction')

    gen.controls(t_start=0, t_end=2.e-8, restart=True)

    gen.parameters(time_between_snapshots=1e-9, initial_timestep=1.e-14)

    gen.add_plot(title='electron temperature', xvars={'time':[],'ir':[0,0]}, yvars={'gamma1_e':[0,1]})

    return gen


name = 'johnrun3'
gen = sim3(2)
print(gen.plots)

#write_run_plot.all(name=name, longprint = False, plot_duplicates=False, object=gen)
#write_run_plot.write(name=name, longprint=False,plot_duplicates=False, object=gen)
#write_run_plot.run(name=name, longprint = False, plot_duplicates=False, object=gen)
#write_run_plot.plot(name=name, longprint = False, plot_duplicates=False, object=gen)
"""
data2 = write_run_plot.extra_plot(name=name, multiplot= True)
title = 'electron temperature'
df = data2[title]
df = df.sort_values(by=['time', 'ir'])

# Your existing code
plt.figure()
heatmap_data = df.pivot_table(index='time', columns='ir', values='tev')

# Handling zeros or negative values in the data
heatmap_data = heatmap_data.replace(0, np.nan)
min_positive = heatmap_data.min().min()
heatmap_data = heatmap_data.fillna(min_positive)
heatmap_data = heatmap_data.clip(lower=min_positive)

# Applying a logarithmic transformation
log_heatmap_data = np.log(heatmap_data)

# Creating the heatmap with the logarithmic data
sns.heatmap(log_heatmap_data)
plt.gca().invert_yaxis()
plt.show()
"""