from importlib import reload
import paths, animate
reload(paths)
import numpy as np
import h5py, os, glob, shutil
import matplotlib.pyplot as plt
import pandas as pd
import io
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


def create_plot(folder_name : str, path:str = paths.to_personal_data(), multiplot : bool = False, logplot : bool = False, make_animation:bool = False):
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
        if num_xvars == 1:
            plot1d(folder, title, df, xvars_set, xvars_in_cols, logplot)

        elif num_xvars == 2:
            plot2d(folder, title, df, xvars_in_cols, logplot, make_animation)

        else:
            raise Exception('must be 2 or less x variables')


def plot1d(folder:str, title:str, df, xvars_set:list, xvars_in_cols:list, logplot:bool):
    xvar = xvars_in_cols[0]
    plt.figure()
    y_labels = []        
    for yvar in df.columns:
        if yvar not in xvars_set:
            plt.plot(df[xvar], df[yvar])
            y_labels.append(yvar)

    if logplot:
        plt.yscale('log')

    plt.xlabel(xvar)
    plt.ylabel(y_labels)
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.savefig(f'{folder}/images/{title}.png')
    plt.close()



def plot2d(folder:str, title:str, df, xvars_in_cols:list, logplot:bool, make_animation:bool):
    if len(df.columns) != 3:
        raise Exception('When using 2 xvariables to create a heatplot, there can only be one yvar since plots can not be overlayd')
    # Plot heatmaps for each combination of x variables and y variables
    xvar1, xvar2 = xvars_in_cols
    yvar = set(df.columns) - set(xvars_in_cols)
    g = f'{folder}/images/{title}_{list(yvar)[0]}_Heatmap'
    g = g.replace(' ','_')

    heatmap_data = df.pivot_table(index=xvar1, columns=xvar2, values=yvar)
    if logplot:
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

    plt.figure()
    sns.heatmap(heatmap_data)
    plt.xlabel(xvar2)
    plt.ylabel(xvar1)
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.savefig(g)
    plt.close()

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