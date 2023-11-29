from importlib import reload
import paths 
reload(paths)
import numpy as np
import h5py, os, glob, shutil
import matplotlib.pyplot as plt


import pandas as pd
import io

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
        data = '\n'.join(lines[2:])
        df = pd.read_csv(io.StringIO(data), delim_whitespace=True, names=columns)
        dataframes[title] = df

    print(dataframes)




def create_plot(folder_name : str, path:str = paths.to_personal_data(), multiplot : bool = False):
    folder = f'{path}{folder_name}'
    global data, start_lines, plot_count
    data, start_lines, plot_count = {},{},0

    parse_data(folder)

    if multiplot:
        return data

    if not os.path.exists(f'{folder}/images'):
        os.makedirs(f'{folder}/images')
        print(f'Created image folder at {folder}/images')


    for key, value in data.items():
        print(key)
        value = np.array(value)
        value = value.astype('float')

        col_count = 0
        for column in value.T:
            if col_count == 0:
                col0 = column
            else:
                plt.plot(col0, column)
            col_count += 1

        plt.title(f'added plot {key}')
        plt.xlabel(key[1])
        plt.ylabel(key[2])
        plt.savefig(f'{folder}/images/{key}.png')
        plt.clf()
        plt.close()

    del data, start_lines, plot_count                    


def plt_path(folder : str):
    os.chdir(folder)
    file_list = glob.glob('*.plt*')
    fullpath = f'{folder}/{file_list[0]}'
    return fullpath