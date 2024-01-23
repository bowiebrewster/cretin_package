import generator_object, write_run_plot, serial_sim_tools, animate, plt_file, to_generator_string


from importlib import reload
for obj in [generator_object, to_generator_string, write_run_plot, serial_sim_tools, animate, plt_file]:
    reload(obj)



def remove(name):
    import os, shutil
    path_rem = f'/home/brewster/Desktop/cretin_package-master/Personal_experiments/{name}/images'

    if os.path.isdir(path_rem):
        print(f'\nremoving {path_rem}')
        shutil.rmtree(path_rem)

def lasfoam_tin(i):

    gen = generator_object.User_input()
    
    rho, T_ev = 0.3, 0.2
    z = 12
    N0, N1 = 1, 101  # We are operating in 1d wih 40 nodes
    Rmin, Rmax = 0, 1.e-4 #node min max max = 10^-4m = 10^5 nm 
    ILASER, TLASER = 1e20, 2.e-9
    wavelength_laser = 2000 #nm

    T_ev = round(T_ev, 5)

    gen.materials_atom(index=1, quantum_n_max=3, element="sn")
    gen.materials_region([N0,N1], elec_temp=T_ev)
    gen.materials_region_rho(rho)
    gen.materials_region_element(initial_ion_population=1.0, index=1)

    gen.geometry(type='slab')
    gen.geometry_nodes(coordinate="r", scaling_type="lin", nodes=[
                       N0, N1], nodes_range=[Rmin, Rmax])

    gen.radiation_ebins(n_boundaries = 61, start = 0.1, end = 10**(5))
    gen.radiation_angles(n_rays = 3)

    gen.controls(t_start=0., t_end = 5e-9, restart = True)

    gen.controls_history(id = 1, value_mutiplier = ILASER, time_multiplier = TLASER)
    gen.controls_history_tv(time = 0., value = 1)
    gen.controls_history_tv(time = 1.0, value = 1.)
    gen.controls_history_tv(time = 1.0, value = 0.)

    gen.parameters(scattering_multiplier = 0,initial_timestep = 10**-13, minimum_timestep = 10**-14, maximum_timestep = 10**-10, time_between_snapshots=10**(-9))

    gen.sources_source_laser(laser_wavelength=4, option_1='rate', option_2='history', values=[1,1.], nodes=[N0, N1])
    gen.popular_switches(continuum_transfer_evolves_temp = True, 
                         )
    gen.other_switches(control_calc_thermal_conduct = 'include thermal conduction', population_calculation = "time dependent diffusion", temperature_calculation = 'use electronic heating rates for time-dependent')
    gen.sources_rswitch(radiation_transfer_algorithm1d= 'do transport using integral formalism', assume_NLTE= True)


    gen.add_plot(title='electron number density', xvars={'time':[],'ir':[0,0]}, yvars={'ne':[0,0]}) #doesn't work 
    gen.add_plot(title='mass density', xvars={'time':[],'ir':[0,0]}, yvars={'zrho':[0,0]})  #doesn't work 

    gen.add_plot(title='electron temperature', xvars={'time':[],'ir':[0,0]}, yvars={'te':[0,0]}) # works
    gen.add_plot(title='net energy gain due to laser absorption', xvars={'time':[],'ir':[0,0]}, yvars={'heatl':[0,0]})  #doesn't work 

    gen.add_plot(title='charge state', xvars={'time':[],'ir':[0,0]}, yvars={'zbar':[0,0]}) #doesn't work 
    gen.add_plot(title='net energy gain due to radiation absorption', xvars={'time':[],'ir':[0,0]}, yvars={'heatj':[0,0]}) #works in log
    gen.add_plot(title='net energy gain due to radiation absorption', xvars={'time':[],'ir':[0,0]}, yvars={'heatt':[0,0]}) #works in log
    gen.add_plot(title='net energy gain due to radiation absorption', xvars={'time':[],'ir':[0,0]}, yvars={'heatl':[0,0]}) #works in log
    gen.add_plot(title='radiation remperature', xvars={'time':[],'ir':[0,0]}, yvars={'tr':[0,0]})#work  
    
    return gen

def do():
    for i in range(1):
    
        name = f'Howard_scott{i}'
        remove(name)
    
        sim4 = lasfoam_tin(2**i)
    
        write_run_plot.write(name = name, object = sim4, longprint=False, plot_duplicates=False)
        #write_run_plot.all(name = name, object = sim4, longprint=False, plot_duplicates=False)
        write_run_plot.run(name = name, object = sim4, longprint=False)
        #write_run_plot.plot(name = name, object = sim4, longprint=False)
        return write_run_plot.extra_plot(name = name, make_animation= True, multiplot = True)
        
stuff = do()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def format_float(value):
    return '{:.3g}'.format(value)


def plot2d(folder:str, title:str, df, xvars_in_cols:list, make_animation:bool):

    # Plot heatmaps for each combination of x variables and y variables
    xvar1, xvar2 = xvars_in_cols
    yvar = set(df.columns) - set(xvars_in_cols)



    heatmap_data = df.pivot_table(index=xvar1, columns=xvar2, values=yvar)
    
    new_columns = [(level1, format_float(level2)) for level1, level2 in heatmap_data.columns]
    print(new_columns)
    
    # Set the new column names
    heatmap_data.columns = pd.MultiIndex.from_tuples(new_columns)
    
    if make_animation:
        g = f'{folder}/images/{title}_{list(yvar)[0]}_anim'
        g = g.replace(' ','_')
        animate.ex_heatmap(heatmap_data, g, xvar2, list(yvar)[0], title) 

    g = f'{folder}/images/{title}_{list(yvar)[0]}_Heatmap'
    g = g.replace(' ','_')

    plt.figure()
    global heato, dfthing
    dfthing = df['time']
    heato = heatmap_data


    sns.heatmap(heatmap_data)
    plt.xlabel(xvar2)
    plt.ylabel(xvar1)
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.show()
    plt.close()
    
plot2d('','',stuff['charge state'], ['ir', 'time'], False)


