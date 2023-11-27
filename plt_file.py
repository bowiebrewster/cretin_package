from importlib import reload
import paths 
reload(paths)
import numpy as np
import h5py, os, glob, shutil
import matplotlib.pyplot as plt

# We use this file to turn existing data structure 


# this is an absolute monstrosity of string manipulation
def restructure(line : str, count : int):
    if line[0] == '#':
        name = line.split(' ')[1]
        start_lines[name] = count

    elif count -1 in start_lines.values():
        global plot_count, vars, data
        plot_count +=1
        vars = line.split('         ')

        vars = [var.strip(' ').strip('$') for var in vars]
        if vars[-1] == '\n':
            vars = vars[0:-1]

        if '\n' in vars[-1]:
            vars[-1] = ' '.join(vars[-1].split('\n')[:-1]).strip(' ')

        vars[0] = vars[0].strip(' ')
        vars = [plot_count] + vars

        vars = tuple(vars)
        data[vars] = []

    if line[0] not in ['$', '#'] and 'vars' in globals():
        line = line.split(' ')
        line[-1] =' '.join(line[-1].split('\n')[:-1])

        newline = []
        for entry in line:
            if len(entry) >3:
                newline.append(entry)

        data[vars].append(newline)

def create_plot(folder_name: str, path: str = paths.to_personal_data(), multiplot: bool = False):
    #Generates plots from data in the specified folder
    folder_path = os.path.join(path, folder_name)
    global start_lines, plot_count
    plot_data, start_lines, plot_count = load_plot_data(folder_path)

    if multiplot:
        return plot_data

    prepare_image_folder(folder_path)
    generate_plots(plot_data, folder_path)



def load_plot_data(folder_path: str):
    #Loads and restructures plot data from the specified folder
    data, start_lines, plot_count = {}, {}, 0

    plt_file_path = get_plot_file_path(folder_path)
    with open(plt_file_path) as file:
        lines = file.readlines()

    for count, line in enumerate(lines):
        restructure(line, count)  # Assuming restructure is a predefined function

    return data, start_lines, plot_count

def get_plot_file_path(folder: str):
    #Finds the full path of the first plot file in the specified folder
    os.chdir(folder)
    file_list = glob.glob('*.plt*')
    return os.path.join(folder, file_list[0])

def prepare_image_folder(folder_path: str):
    #Creates or cleans an image folder at the specified path
    image_folder_path = os.path.join(folder_path, 'images')
    if os.path.exists(image_folder_path):
        shutil.rmtree(image_folder_path)
        print('Removed existing image folder')
    os.makedirs(image_folder_path)
    print(f'Created image folder at {image_folder_path}')

def generate_plots(data, folder_path):
    #Generates and saves plot images using the provided data
    image_folder_path = os.path.join(folder_path, 'images')

    for key, value in data.items():
        value = np.array(value).astype('float')
        plot_and_save(value, key, image_folder_path)

def plot_and_save(value, key, image_folder_path):
    #Plots and saves a single plot to the specified path
    for col_count, column in enumerate(value.T):
        if col_count == 0:
            col0 = column
        else:
            plt.plot(col0, column)

    plt.title(f'Added plot {key}')
    plt.xlabel(key[1])
    plt.ylabel(key[2])
    plt.savefig(os.path.join(image_folder_path, f'{key}.png'))
    plt.clf()
    plt.close()