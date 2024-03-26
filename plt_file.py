# for plotting .plt files created by cretin as output


import paths, animate, os, glob, io
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

xvars = 'cycle,iter,time,ir,r,cdens,x2d,y2d,z2d,x3d,y3d,z3d,xy,k,kx,ky,kz,kr,l,lx,ly,lz,lr,m,mx,my,mz,mr,ifr,energy,freq,wvl,ebins,fbins,wbins,ifrline,evline,isp,sp_energy,sp_freq,sp_nu,sp_wvl,ie,iso,level,elev'


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
            plot1d(folder, title, df, xvars_set, df.columns)
   
        elif num_xvars == 1:
            plot1d(folder, title, df, xvars_set, xvars_in_cols)

        elif num_xvars == 2:
            plot2d(folder, title, df, xvars_set, xvars_in_cols, make_animation)

        else:
            raise Exception('too many xvariables')


def plot1d(folder:str, title:str, df, xvars_set:list, xvars_in_cols:list):
    xvar = xvars_in_cols[0]
    plt.figure()
    y_labels = []        
    for yvar in df.columns:
        if yvar not in xvars_set:
            plt.plot(df[xvar], df[yvar])
            y_labels.append(yvar)

    if 'log' in title[-3:]:
        plt.yscale('log')

    plt.xlabel(xvar)
    plt.ylabel(y_labels)
    plt.legend(y_labels)
    plt.title(title)

    plt.savefig(f'{folder}/images/{title}.png')
    plt.close()

def format_float(value):
    return '{:.3g}'.format(value)

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

def plot2d(folder:str, title:str, df, xvars_set: list, xvars_in_cols:list, make_animation:bool):
    if len(df.columns) < 3:
        plot1d(folder, title, df, xvars_set, df.columns[0])
        return
    if len(df.columns) > 3:
        raise Exception('When using 2 xvariables to create a heatplot, there can only be one yvar since plots can not be overlayd')
    # Plot heatmaps for each combination of x variables and y variables
    xvar1, xvar2 = xvars_in_cols
    yvar = set(df.columns) - set(xvars_in_cols)


    heatmap_data = df.pivot_table(index=xvar1, columns=xvar2, values=yvar)
    times, heatmap_data = select_time_intervals(heatmap_data)
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
            animate.ex_heatmap(heatmap_data, g, xvar2, list(yvar)[0], title) 

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
        plot1d(folder, title, df.iloc[0, :], xvars_set, xvars_in_cols)
        return False

    # Check if all rows have approximately the same values
    all_rows_same = all(np.allclose(df.loc[row], df.iloc[0, :], atol=tolerance) for row in df.index)
    if all_rows_same:
        print(f'{title} has identical rows and has been projected down 1 dimension')
        plot1d(folder, title, df.iloc[:, 0], xvars_set, xvars_in_cols)
        return False

    return True

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
    
def plt_path(folder : str):
    os.chdir(folder)
    file_list = glob.glob('*.plt*')
    fullpath = f'{folder}/{file_list[0]}'
    return fullpath