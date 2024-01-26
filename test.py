import generator_object, write_run_plot, serial_sim_tools, animate, plt_file, to_generator_string


from importlib import reload
for obj in [generator_object, to_generator_string, write_run_plot, serial_sim_tools, animate, plt_file]:
    reload(obj)

def lasfoam_tin(i):

    gen = generator_object.User_input()
    
    rho, T_ev = round(i*1,3), .6
    print(rho)
    z = 12. #
    N0, N1 = 1, 501  # We are operating in 1d wih 100 nodes
    Rmin, Rmax = 0, 30.e-4 #node min max max = 10^-6m = 30 micron 
    ILASER, TLASER = 1e18, 1.e-9 #corresponds to 10^11 W/cm^2
    wavelength_laser = 1 # corresponds to 2*1.06 micrometer

    gen.materials_atom(index = 1, quantum_n_max = 3, element = "sn")
    gen.materials_region([N0,N1], elec_temp = T_ev)
    gen.materials_region_rho(rho)
    gen.materials_region_element(initial_ion_population = 1.0, index = 1)

    gen.geometry(type='slab')
    gen.geometry_nodes(coordinate = "r", scaling_type = "lin", nodes = [N0, N1], nodes_range = [Rmin, Rmax])

    gen.radiation_ebins(n_boundaries = 61, start = 0.1, end = 10**(5))
    gen.radiation_angles(n_rays = 3)

    gen.controls(t_start = 0., t_end = 3e-9, restart = True)

    gen.controls_history(id = 1, value_mutiplier = ILASER, time_multiplier = TLASER)
    gen.controls_history_tv(time = 0., value = 1)
    gen.controls_history_tv(time = 1.0, value = 1.)
    gen.controls_history_tv(time = 1.0, value = 0.)

    gen.sources_source_laser(laser_wavelength = wavelength_laser, option_1 = 'rate', option_2 = 'history', values = [1,1.], nodes = [N0, round(N1/10)])
    gen.parameters(scattering_multiplier = 0,initial_timestep = 10**-13, minimum_timestep = 10**-16, maximum_timestep = 10**-10, time_between_snapshots = 10**(-9))

    gen.popular_switches(continuum_transfer_evolves_temp = True,
                         mesh_treatment = 'staggered centering (node + zones)')
    gen.other_switches(control_calc_thermal_conduct = 'include thermal conduction', 
                       population_calculation = "time dependent diffusion", 
                       temperature_calculation = 'use electronic heating rates for time-dependent')
    
    gen.sources_rswitch(radiation_transfer_algorithm1d= 'do transport using integral formalism', assume_NLTE= True)

    gen.add_plot(title='electron number density', xvars={'time':[],'ir':[0,0]}, yvars={'ne':[0,0]})
    gen.add_plot(title='mass density', xvars={'time':[],'ir':[0,0]}, yvars={'zrho':[0,0]})  
    gen.add_plot(title='charge state', xvars={'time':[],'ir':[0,0]}, yvars={'zbar':[0,0]}) 

    gen.add_plot(title='electron temperature', xvars={'time':[],'ir':[0,0]}, yvars={'tev':[0,0]})
    gen.add_plot(title='radiation remperature', xvars={'time':[],'ir':[0,0]}, yvars={'trv':[0,0]}) 

    gen.add_plot(title='net energy gain due to laser absorption', xvars={'time':[],'ir':[0,0]}, yvars={'heatl':[0,0]})  
    gen.add_plot(title='net energy gain due to radiation absorption', xvars={'time':[],'ir':[0,0]}, yvars={'heatj':[0,0]}) 
    gen.add_plot(title='Net free electron heating rate due to all processes', xvars={'time':[],'ir':[0,0]}, yvars={'heatt':[0,0]}) 

    return gen

import paths, os, glob
xvars = 'cycle,iter,time,ir,r,cdens,x2d,y2d,z2d,x3d,y3d,z3d,xy,k,kx,ky,kz,kr,l,lx,ly,lz,lr,m,mx,my,mz,mr,ifr,energy,freq,wvl,ebins,fbins,wbins,ifrline,evline,isp,sp_energy,sp_freq,sp_nu,sp_wvl,ie,iso,level,elev'


def extra_plot(name : str, multiplot : bool = False, make_animation:bool = False):
    p = f'{paths.to_personal_data()}{name}/{name}.plt'
    if os.path.exists(p):
        return create_plot(folder_name = name, multiplot = multiplot, make_animation = make_animation)

def plt_path(folder : str):
    os.chdir(folder)
    file_list = glob.glob('*.plt*')
    fullpath = f'{folder}/{file_list[0]}'
    return fullpath

def make_unique(columns:list):
    if len(set(columns)) == len(columns):
        return columns
    else:
        newcols = []
        for index, col in enumerate(columns):
            if col in xvars.split(","):
                newcols.append(col)
            else:
                newcols.append(col + str(index))

        return newcols 

def parse_data(folder_path):
    file_path = plt_path(folder_path)

    with open(file_path, 'r') as file:
        text = file.read()
    sections = text.split('#')[1:]  # Split by sections, ignore first empty part
    dataframes = {}

    for section in sections:
        lines = section.strip().split('\n')
        title = lines[0].strip()
        columns = lines[1].strip().split()[1:]  # Ignore the dollar sign
        columns = make_unique(columns)
        data = '\n'.join(lines[3:])
        df = pd.read_csv(io.StringIO(data), delim_whitespace=True, names=columns)
        dataframes[title] = df

    return(dataframes)


def create_plot(folder_name : str, path:str = paths.to_personal_data(), multiplot : bool = False, make_animation:bool = False):
    folder = f'{path}{folder_name}'
    global data, start_lines, plot_count
    data, start_lines, plot_count = {},{},0

    data = parse_data(folder)

    if multiplot:
        return data
    
    print(f'adding additional plot to {folder}/images')
    if not os.path.exists(f'{folder}/images'):
        os.makedirs(f'{folder}/images')
        print(f'Created image folder at {folder}/images')

    # Define x variables
    xvars_set = set(xvars.split(","))
    for title, df in data.items():
        # Check which columns in df are x variables
        xvars_in_cols = [col for col in df.columns if col in xvars_set]
        # Count the number of x variables in df
        num_xvars = len(xvars_in_cols)

        if num_xvars == 0:
            #plot1d(folder, title, df, xvars_set, df.columns)
            pass
   
        elif num_xvars == 1:
            #plot1d(folder, title, df, xvars_set, xvars_in_cols)
            pass

        elif num_xvars == 2:
            plot2d(folder, title, df, xvars_set, xvars_in_cols, make_animation)
            pass

        else:
            raise Exception('too many xvariables')
        
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import seaborn as sns

def plott2d_check(folder: str, title: str, df: pd.DataFrame, xvars_set: list, xvars_in_cols: list):
    # Set a tolerance for comparing floating-point numbers
    tolerance = 1e-5

    # Check if entire DataFrame has approximately the same value
    if np.allclose(df.to_numpy(), df.iloc[0, 0], atol=tolerance):
        print(f'{title} is a constant matrix and has not been plotted.')
        return False

    # Check if all columns have approximately the same values
    all_columns_same = all(np.allclose(df[col], df.iloc[:, 0], atol=tolerance) for col in df.columns)
    if all_columns_same:
        print(f'{title} has identical columns and has been projected down 1 dimension')
        #plot1d(folder, title, df.iloc[0, :], xvars_set, xvars_in_cols)
        return False

    # Check if all rows have approximately the same values
    all_rows_same = all(np.allclose(df.loc[row], df.iloc[0, :], atol=tolerance) for row in df.index)
    if all_rows_same:
        print(f'{title} has identical rows and has been projected down 1 dimension')
        #plot1d(folder, title, df.iloc[:, 0], xvars_set, xvars_in_cols)
        return False

    return True



def plot2d(folder:str, title:str, df, xvars_set: list, xvars_in_cols:list, make_animation:bool):
    if len(df.columns) < 3:
        #plot1d(folder, title, df, xvars_set, df.columns[0])
        return
    if len(df.columns) > 3:
        raise Exception('When using 2 xvariables to create a heatplot, there can only be one yvar since plots can not be overlayd')
    # Plot heatmaps for each combination of x variables and y variables
    xvar1, xvar2 = xvars_in_cols
    yvar = set(df.columns) - set(xvars_in_cols)

    global heatmap_data
    heatmap_data = df.pivot_table(index=xvar1, columns=xvar2, values=yvar)
    formatted_index = heatmap_data.index.map(format_float)

    # Set the new formatted index
    heatmap_data.index = pd.Index(formatted_index)
    if plott2d_check(folder, title, df, xvars_set, xvars_in_cols):
        if 'log' in title[-3:]:
            # Handling zeros or negative values in the data
            heatmap_data = heatmap_data.replace(0, np.nan)
            min_positive = heatmap_data.min().min()
            heatmap_data = heatmap_data.fillna(min_positive)
            heatmap_data = heatmap_data.clip(lower=min_positive)

            # Applying a logarithmic transformation
            heatmap_data = np.log(heatmap_data)
        if make_animation:
            g = f'{folder}/images/{title}_{list(yvar)[0]}_anim'
            g = g.replace(' ','_')
            ex_heatmap(heatmap_data, g, xvar2, list(yvar)[0], title) 

        g = f'{folder}/images/{title}_{list(yvar)[0]}_Heatmap'
        g = g.replace(' ','_')

        # Calculate percentiles for color scale clipping
        lower_percentile = np.percentile(heatmap_data.to_numpy(), 5)  # 5th percentile
        upper_percentile = np.percentile(heatmap_data.to_numpy(), 95) # 95th percentile

        # Plotting
        plt.figure()
        sns.heatmap(heatmap_data, vmin=lower_percentile, vmax=upper_percentile)  # Adjusted color scaling

        plt.xlabel(xvar2)
        plt.ylabel(xvar1)
        plt.title(title)
        plt.gca().invert_yaxis()
        plt.savefig(g)
        plt.close()
from matplotlib.animation import FuncAnimation

def ex_heatmap(df, path, xvar1, yvar, title) :

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)

    # Set the x-axis to match the column names (positions)
    try:
        positions = df.columns.astype(float)
    except:
        df.columns = df.columns.get_level_values(1)
        positions = df.columns.astype(float)

    def init():
        y_min = df.values.min()
        y_max = df.values.max()
        if abs(y_min - y_max) < 1.e-4:
            y_min, y_max = (y_min - 1)*.99, (y_max + 1)*1.01  # Adjust these values as appropriate for your data

        ax.set_xlim(positions.min(), positions.max())
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(xvar1)
        ax.set_ylabel(yvar)
        ax.set_title(title)
        return line,

    # Update function for each frame
    def update(frame):
        line.set_data(positions, df.iloc[frame])
        return line,

    print('reached')
    # Create animation
    #ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True)

    # Save the animation
    #ani.save(path+'.mp4', writer='ffmpeg', fps=32)
    #plt.close()
    

import pandas as pd

def select_time_intervals(df, num_intervals=600):
    # Convert the index to a numpy array of floats, handling errors
    try:
        time_values = pd.to_numeric(df.index, errors='raise').to_numpy()
    except ValueError:
        raise ValueError("The index contains values that cannot be converted to numeric type.")

    # Determine the start and end times from the index
    t_0 = time_values[0]
    t_end = time_values[-1]

    # Calculate the interval
    interval = (t_end - t_0) / num_intervals
    print(interval)

    # Find rows closest to each interval
    selected_indices = []
    for i in range(num_intervals):
        target_time = t_0 + i * interval
        # Find the index closest to the target_time
        closest_index = np.abs(time_values - target_time).argmin()
        selected_indices.append(df.index[closest_index])

    
    
    # Remove duplicates and sort the indices
    selected_indices = sorted(set(selected_indices))
    
    # Select rows from the original DataFrame using loc
    selected_df = df.loc[selected_indices]

    return selected_indices, selected_df

# Example usage
# Assuming 'df' is your original DataFrame
# reduced_df = select_time_intervals(df)


def format_float(value):
    return '{:.3g}'.format(value)

for i in range(1):
    sim4 = lasfoam_tin(1.2**i)
    name = f'Howard_scott32_{i}'
    #write_run_plot.write(name = name, object = sim4, longprint=False, plot_duplicates=False)
    #write_run_plot.all(name = name, object = sim4, longprint=False, plot_duplicates=False)
    #write_run_plot.run(name = name, object = sim4, longprint=False)
    #write_run_plot.plot(name = name, object = sim4, longprint=False)
    #extra_plot(name = name, make_animation=True)