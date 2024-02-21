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
with open(f"{paths.to_folder_cretin()}key_naming.json", 'r') as file:
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

def dump_path(name,  newpath:str= None):
    if newpath == None:
        path = os.path.join(paths.to_personal_data(), name)
    else:
        path = os.path.join(newpath, name)
    os.chdir(path)
    file_list = glob.glob('*.d*') + glob.glob('*.s*')
    return os.path.join(path, file_list[0])


def split(name : str):
    splitname = name.split('_')
    key = splitname[0]
    index = '_'.join(splitname[1:])
    return key, index

def blacklist_key(key : str):
    if key.split('_')[0] in [ 'u', 'r']:
        return True
    else:
        return False

def plot(name, longprint=False, plot_duplicates=False, object = None, newpath:str= None):
    if newpath == None:
        fullpath = dump_path(name)
    else:
        fullpath = dump_path(name, newpath)
    
    path = os.path.join(paths.to_personal_data(), name, 'images')
    print(f'plotting {name} to {path}')
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    #save_h5_to_txt(fullpath, 'output8')
    cons_dict = {}
    with h5py.File(fullpath, 'r') as f:
        plot_data(f, path, longprint, plot_duplicates, cons_dict)

    # Open a file in write mode ('w') in the current directory
    with open('constant_values.txt', 'w') as text_file:
        for key, value in cons_dict.items():
            text_file.write(f'{key}: {value}\n')

def plot_data(h5obj, path, longprint, plot_duplicates, cons_dict, indent=0):
    arrays0d, arrays1d, arrays2d = {}, {}, {}
    for key in h5obj.keys():
        if longprint:
            print('  ' * indent + key)  # Print the current group/dataset name with indentation
        if isinstance(h5obj[key], h5py.Group):
            # Pass cons_dict to the recursive call to ensure updates are propagated
            plot_data(h5obj[key], path, longprint, plot_duplicates, cons_dict, indent + 1)

        else:
            # If it's a dataset, process and plot its data
            try:
                arr = np.array(h5obj[key])
                arr = np.squeeze(arr)
                dim = len(arr.shape)
                if is_real_array(arr) and not blacklist_key(key):
                    handle_plotting(arr, dim, key, path, longprint, plot_duplicates, arrays0d, arrays1d, arrays2d, indent)
                else:
                    if longprint:
                        print('  ' * (indent + 1) + f'Invalid array found with key {key}')
            except Exception as e:
                print(f'Error processing dataset {key}: {e}')
    if arrays0d:
        try:
            cons_dict.update(arrays0d) 
        except:
            print(f'tried to be added but was not a valid dict {arrays0d}')




def save_h5_to_txt(h5_path, txt_path):
    with h5py.File(h5_path, 'r') as f, open(txt_path, 'w') as txt_file:
        def save_items(h5obj, indent=0):
            for key in h5obj.keys():
                # Print the key, which could be a group or a dataset name
                txt_file.write('  ' * indent + key + '\n')
                if isinstance(h5obj[key], h5py.Group):
                    # If it's a group, recursively save its contents
                    save_items(h5obj[key], indent + 1)
                else:
                    # If it's a dataset, save its data
                    # Set print options to ensure full array is printed
                    with np.printoptions(threshold=np.inf):
                        data = h5obj[key][...]
                        txt_file.write('  ' * (indent + 1) + str(data) + '\n\n')

        # Save all groups and datasets
        save_items(f)


def handle_plotting(arr, dim, key, path, longprint, plot_duplicates, arrays0d, arrays1d, arrays2d, counter):
    if dim == 0:
        arrays0d[key] = arr.item()
    elif dim == 1 and len(arr) > 0:
        if np.all(arr == arr[0]):  # Check if all values in the array are the same
            # If it's a constant array, add to the dictionary
            arrays0d[key] = arr[0]
        else:
            # Proceed with plotting for non-constant 1D arrays
            plot1d(path, key, longprint, plot_duplicates, arr, arrays2d)
    elif dim == 2:
        plot2d(path, key, longprint, plot_duplicates, arr, arrays2d)
    elif longprint:
        print(f'{key} has shape {arr.shape} and has not been plotted')

def plot1d(path, key, longprint, plot_duplicates, arr, arrays):
    if should_plot(arr, arrays, plot_duplicates, longprint):

        plt.plot(arr)
        plt.title(get_title(key))
        plt.savefig(os.path.join(path, f'{get_title(key)}.png'), dpi=800)
        plt.clf()
        plt.close()
        arrays[key] = arr

def plot2d(path, key, longprint, plot_duplicates, arr, arrays):
    collapse = check_if_vectors_identical(arr)
    if collapse in ['rows', 'columns']:
        vector = arr[0] if collapse == 'rows' else arr[:, 0]
        plot1d(path, key, longprint, plot_duplicates, vector, arrays)
    else:
        if should_plot_2d(arr, arrays, plot_duplicates, longprint, key):
            plot_and_save_2d(arr, path, key)

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

def should_plot_2d(arr, arrays, plot_duplicates, longprint, masterkey):
    return True
    #for key, array in arrays.items():
    #    if np.shape(array) == np.shape(arr) and np.allclose(arr, array):
    #        if longprint:
    #            print(f"{masterkey} is identical to other array")
    #        return False
    #return plot_duplicates or not arrays

def plot_and_save_2d(arr, path, masterkey):

    fig, ax = plt.subplots()

    # Plot the array
    im = ax.imshow(arr)

    aspect_ratio = arr.shape[1] / arr.shape[0]  # columns / rows
    ax.set_aspect(aspect_ratio)

    # Add color bar
    plt.colorbar(im, ax=ax)

    # Set the title
    plt.title(get_title(masterkey))

    # Save the figure
    plt.savefig(os.path.join(path, f'{get_title(masterkey)}.png'))

    # Close the figure
    plt.close(fig)


def select_ticks(ticks, max_ticks=10):
    """Select a subset of ticks to display, rounded to two significant digits."""
    if len(ticks) <= max_ticks:
        return np.around(ticks, 2)
    step = len(ticks) // max_ticks
    return np.around(ticks[::step], 2)


def should_plot(arr, arrays, plot_duplicates, longprint):
    for key, array in arrays.items():
        if np.shape(array) == np.shape(arr) and np.allclose(arr, array):
            if longprint:
                print(f"{key} is identical to other array")
            return False
    return True

def is_real_array(arr):
    # Check if it's a list and try to convert it to a NumPy array
    if isinstance(arr, list):
        try:
            arr = np.array(arr)
        except ValueError:
            # If conversion fails, return False
            return False
    
    # Check if it's a NumPy array
    if not isinstance(arr, np.ndarray):
        return False

    # Check if the array's data type is floating-point or integer
    if not (np.issubdtype(arr.dtype, np.floating) or np.issubdtype(arr.dtype, np.integer)):
        return False
    
    return True

def get_title(key):
    splitname = key.split('_')
    name = splitname[0]
    index = '_'.join(splitname[1:])
    return naming_dict.get(name, name) + index

def extra_plot(name : str, multiplot : bool = False, make_animation:bool = False):
    import plt_file
    p = f'{paths.to_personal_data()}{name}/{name}.plt'
    if os.path.exists(p):
        return plt_file.create_plot(folder_name = name, multiplot = multiplot, make_animation = make_animation)
        

def all(name, object, longprint=False, plot_duplicates=False):
    write(name, object)
    run(name, longprint)
    plot(name, longprint, plot_duplicates)
    extra_plot(name)