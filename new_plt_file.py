from importlib import reload
import paths 
reload(paths)
import numpy as np
import h5py, os, glob, shutil
import matplotlib.pyplot as plt
import pandas as pd
import io
import seaborn as sns

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
        data = '\n'.join(lines[3:])
        df = pd.read_csv(io.StringIO(data), delim_whitespace=True, names=columns)
        dataframes[title] = df

    return(dataframes)


def create_plot(folder_name : str, path:str = paths.to_personal_data(), multiplot : bool = False):
    folder = f'{path}{folder_name}'
    global data, start_lines, plot_count
    data, start_lines, plot_count = {},{},0

    data = parse_data(folder)
    print(f'adding additional plot to {folder}')
    if multiplot:
        return data

    if not os.path.exists(f'{folder}/images'):
        os.makedirs(f'{folder}/images')
        print(f'Created image folder at {folder}/images')

    # Define x variables
    xvars = 'cycle,iter,time,ir,r,cdens,x2d,y2d,z2d,x3d,y3d,z3d,xy,k,kx,ky,kz,kr,l,lx,ly,lz,lr,m,mx,my,mz,mr,ifr,energy,freq,wvl,ebins,fbins,wbins,ifrline,evline,isp,sp_energy,sp_freq,sp_nu,sp_wvl,ie,iso,level,elev'
    xvars_set = set(xvars.split(","))
    for title, df in data.items():
        print(title, df.columns)
        # Check which columns in df are x variables
        xvars_in_cols = [col for col in df.columns if col in xvars_set]

        # Count the number of x variables in df
        num_xvars = len(xvars_in_cols)

        # Raise exceptions based on the number of x variables
        if num_xvars == 0:
            raise Exception('Zero x variables in .plt file')
        elif num_xvars == 1:
            # Plot each y variable against the x variable
            xvar = xvars_in_cols[0]
            plt.figure()
            y_labels = []        
            for yvar in df.columns:
                if yvar not in xvars_set:
                    plt.plot(df[xvar], df[yvar])
                    y_labels.append(yvar)
            plt.xlabel(xvar)
            plt.ylabel(y_labels)
            plt.title(title)
            plt.savefig(f'{folder}/images/{title}.png')
            plt.close()   

        elif num_xvars == 2:
            if len(df.columns) != 3:
                raise Exception('When using 2 xvariables to create a heatplot, there can only be one yvar since plots can not be overlayd')
            # Plot heatmaps for each combination of x variables and y variables
            xvar1, xvar2 = xvars_in_cols
            for yvar in df.columns:
                if yvar not in xvars_set:
                    plt.figure()
                    heatmap_data = df.pivot_table(index=xvar1, columns=xvar2, values=yvar)
                    sns.heatmap(heatmap_data)
                    plt.xlabel(xvar2)
                    plt.ylabel(xvar1)
                    g = f'{folder}/images/{title}_{yvar}_Heatmap'
                    plt.title(g)
                    plt.savefig(g)
                    print(f"printing to {g}")
                    plt.close()
        else:
            raise Exception('Too many x variables')
        



def plt_path(folder : str):
    os.chdir(folder)
    file_list = glob.glob('*.plt*')
    fullpath = f'{folder}/{file_list[0]}'
    return fullpath