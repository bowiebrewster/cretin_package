from importlib import reload
import numpy as np
import matplotlib.pyplot as plt
import h5py, os, glob, shutil, subprocess, json
import generator_object, to_generator_string, search, paths,plt_file #these python classes should be in the same folder as cretin_main
for obj in [generator_object, to_generator_string, search, paths, plt_file]:
    reload(obj)

# this file takes the string created by to_generator_string.py and writes it to a file, runs creting with that file, and parses and plots the data created by cretin. 
# note not every of the above mentioned functions has to be run in series (although that is what write_run_plot.all()) does. If you want to make changes to the .gen file for example
# feel free not to overwrite it, and if the data is already where you want it to be feel free to only call plot. 

# Open the file and parse the JSON content
with open(f"{paths.to_folder_cretin()}/key_naming.txt", 'r') as file:
    naming_dict = json.load(file)

# takes the text string and writes it to the cretin generator file
def write(name : str, object, longprint = None, plot_duplicates = None):
    string = to_generator_string.Text_generator(object).execute()
    directory = os.path.join(paths.to_personal_data(), name)

    if not os.path.exists(directory):
        os.makedirs(directory)


    file_path = os.path.join(directory, f'{name}.gen')
    print(f'\nwriting to {file_path}')
    with open(file_path, 'w') as file:
        file.writelines(map(str, string))

#  running cretin using the written generator file
def run(name : str, longprint : bool, object = None, plot_duplicates = None, newpath:str = None):
    print(f'running cretin with {name}')
    import subprocess

    env = os.environ.copy()
    if newpath == None:
        path = f'{paths.to_personal_data()}{name}'
    else:
        path = f'{newpath}{name}'


    env["ARG_NAME0"] = name
    env["ARG_NAME1"] = path
    env["CRETIN_BIN_DIR"] = paths.to_cretin_ex()

    process = subprocess.Popen(paths.to_folder_cretin() + 'demo.sh', shell = True , stdout = subprocess.PIPE, stderr = subprocess.PIPE, env = env)
    process.wait() # Wait for process to complete.
    out, err = process.communicate()

    if longprint: print(out.decode())
    if len(err.decode()) > 0: print("ERROR:",err.decode())

def dump_path(name):
    path = os.path.join(paths.to_personal_data(), name)
    os.chdir(path)
    file_list = glob.glob('*.d0*')
    return os.path.join(path, file_list[0])


def split(name : str):
    splitname = name.split('_')
    key = splitname[0]
    index = '_'.join(splitname[1:])
    return key, index

def blacklist_key(key : str):
    if key in ['previous','ai','zi']:
        return True
    elif key.split('_')[0] in ['model','r', 'u', 'regmap', 'iso']:
        return True
    else:
        return False

def plot(name, longprint=False, plot_duplicates=False, object = None):
    fullpath = dump_path(name)
    path = os.path.join(paths.to_personal_data(), name, 'images')
    print(f'plotting {name} to {path}')
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    with h5py.File(fullpath, 'r') as f:
        plot_data(f, path, longprint, plot_duplicates)

def plot_data(file, path, longprint, plot_duplicates):
    arrays2d, arrays3d = {}, {}
    for i, key in enumerate(file.keys()):
        arr = np.array(file[key])
        dim = len(arr.shape)
        handle_plotting(arr, dim, key, path, longprint, plot_duplicates, arrays2d, arrays3d, i)

def handle_plotting(arr, dim, key, path, longprint, plot_duplicates, arrays2d, arrays3d, counter):
    if dim == 1 and len(arr) > 0:
        plot1d_or_2d(path, key, longprint, plot_duplicates, arr, arrays2d)
    elif dim == 2:
        plot1d_or_2d(path, key, longprint, plot_duplicates, arr, arrays2d)
    elif dim == 3:
        plot3d(path, key, longprint, plot_duplicates, arr, arrays3d)
    elif longprint:
        print(f'{key} has shape {arr.shape} and has not been plotted')

def plot1d_or_2d(path, key, longprint, plot_duplicates, arr, arrays):
    if should_plot(arr, arrays, plot_duplicates, longprint):
        plt.plot(arr)
        plt.title(get_title(key))
        plt.savefig(os.path.join(path, f'{get_title(key)}.png'), dpi=800)
        plt.clf()
        plt.close()
        arrays[key] = arr

def plot3d(path, key, longprint, plot_duplicates, arr, arrays):
    collapse = check_if_vectors_identical(arr)
    if collapse in ['rows', 'columns']:
        vector = arr[0] if collapse == 'rows' else arr[:, 0]
        plot1d_or_2d(path, key, longprint, plot_duplicates, vector, arrays)
    else:
        if should_plot_3d(arr, arrays, plot_duplicates, longprint, key):
            plot_and_save_3d(arr, path, key)

def check_if_vectors_identical(arr):
    if arr.shape[0] < 1:
        return False
    
    ref_vector = arr[0]
    ref_column = arr[:, 0]

    if np.all(np.equal(arr, ref_vector), axis=1).all():
        return 'rows'
    elif np.all(np.equal(arr, ref_column.reshape(-1, 1)), axis=0).all():
        return 'columns'
    else:
        return None

def should_plot_3d(arr, arrays, plot_duplicates, longprint, masterkey):
    for key, array in arrays.items():
        if np.shape(array) == np.shape(arr) and np.allclose(arr, array):
            if longprint:
                print(f"{masterkey} is identical to other array")
            return False
    return plot_duplicates or not arrays

def plot_and_save_3d(arr, path, masterkey):
    fig, ax = plt.subplots()
    im = ax.imshow(arr)
    plt.title(get_title(masterkey))
    plt.colorbar(im, ax=ax)
    plt.savefig(os.path.join(path, f'{get_title(masterkey)}.png'))
    plt.close(fig)


def should_plot(arr, arrays, plot_duplicates, longprint):
    for key, array in arrays.items():
        if np.shape(array) == np.shape(arr) and np.allclose(arr, array):
            if longprint:
                print(f"{key} is identical to other array")
            return False
    return True

def get_title(key):
    splitname = key.split('_')
    name = splitname[0]
    index = '_'.join(splitname[1:])
    return naming_dict.get(name, name) + index

def extra_plot(name, multiplot=False):
    plt_file.create_plot(folder_name=name, multiplot=multiplot)

def all(name, object, longprint=False, plot_duplicates=False):
    write(name, object)
    run(name, longprint)
    plot(name, longprint, plot_duplicates)
    extra_plot(name)