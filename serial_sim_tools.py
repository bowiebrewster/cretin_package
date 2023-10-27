
import os, h5py, glob, shutil
from importlib import reload
import numpy as np
import generator_object, to_generator_string, search, paths, write_run_plot, plt_file
import matplotlib.pyplot as plt

for obj in [generator_object, to_generator_string, search, paths, write_run_plot, plt_file]:
    reload(obj)
naming_dict = write_run_plot.naming_dict

# in this file we have all the functions for serial simulations. 


# takes as an arugment a (jagged) array consisting of k vectors of size k_i
# returns all possible combinations of the entries in those vectors. 
# for example input array = [[a1,a2,a3],[b1,b2]] returns [[a1,b1],[a1,b2],[a2,b1],[a2,b2],[a3,b1],[a3,b2]]
def combinatorics(arr):
    if len(arr) == 0:
        return [[]]
    else:
        result = []
        for item in arr[0]:
            for combination in combinatorics(arr[1:]):
                result.append([item] + combination)
        return result
    
# extracting the data from the dumpfile
def savedict(path : str):
    dictio = {}
    with h5py.File(path, 'r') as f:
        for key in f.keys():
            arr = np.array(f[key])
            dictio[key] = arr
    return dictio

all_trials_dict = {}

def plot_all(foldername : str, trials : list):
    for trial in trials:
        global arrays2d, arrays3d
        arrays2d, arrays3d = {}, {}
        plot(trial, plot_duplicates = False)
        all_trials_dict[trial] = [arrays2d, arrays3d]

    # we love list comprehesion
    keys2d = all_trials_dict[trials[0]][0].keys()
    keys3d = all_trials_dict[trials[0]][1].keys()
    keys2d = [list(all_trials_dict[trial][0].keys()) for trial in trials]
    keys3d = [list(all_trials_dict[trial][1].keys()) for trial in trials]
    set_2d = set([item for sublist in keys2d for item in sublist])
    set_3d = set([item for sublist in keys3d for item in sublist])

    path = f'{paths.to_personal_data()}{foldername}'
    print(f'multiplot to {path}')
    if os.path.exists(path):
        shutil.rmtree(path) 
    os.mkdir(path)

    if len(keys2d) >0:
        for key in set_2d:
            all(path, key, trials)

    if len(keys3d) >0:
        for key in set_3d:
            all(path, key, trials)

    plt_files(path, trials)

def plot(name : str, plot_duplicates : bool):
    # finding d file
    path_test = paths.to_personal_data()
    os.chdir(path_test + '/' + name)
    file_list = glob.glob('*.d*')

    if len(file_list) == 0:
        raise Exception(f'{name} file list does not contain dump file but does contain {os.listdir()}')
    fullpath = f'{path_test}/{name}/{file_list[0]}'

    with h5py.File(fullpath, 'r') as f:
        # managing directories
        path = path_test + name + '/images'
        if os.path.exists(path):
            shutil.rmtree(path) 
        os.mkdir(path)
            
        for key in f.keys():
            arr = np.array(f[key])

            if write_run_plot.blacklist_key(key) or len(arr.shape) == 0:
                pass

            elif len(arr.shape) == 2:
                plot3d(key, plot_duplicates, arr)

            elif len(arr.shape) == 1 and len(arr) > 0:
                plot2d(key, plot_duplicates, arr)

            else:
                print(f'strange array with shape {arr.shape} has not been plot')

def plot2d(masterkey:str,  plot_duplicates : bool, arr):
    save_bool = True 
    for array in arrays2d.values():
        if np.shape(array) == np.shape(arr):
            if np.allclose(arr, array):
                save_bool = False
               
    if save_bool or plot_duplicates:
        arrays2d[masterkey] = arr

def plot3d(masterkey : str,  plot_duplicates : bool, arr):
    collapse = are_all_vectors_identical(arr)
    if collapse == 'rows':
        vector = arr[0]
        plot2d(masterkey, plot_duplicates, vector)
    elif collapse == 'columns':
        vector = arr[:, 0]
        plot2d(masterkey, plot_duplicates, vector)

    else:        
        save_bool = True
        for array in arrays3d.values():
            if np.shape(array) == np.shape(arr):
                if np.allclose(arr, array):
                    save_bool = False
                    
        if save_bool or plot_duplicates:
            arrays3d[masterkey] = arr

def all(path: str, key: str, trials:list):
    legend = []
    has_plot = False
    for trial in trials:
        trial_dict = all_trials_dict[trial][0]
        if key in trial_dict.keys():
            arr = trial_dict[key]
            plt.plot(arr)
            has_plot = True
            legend.append(trial)


    key, index = write_run_plot.split(key)

    if key in axis_dict.keys():
        plt.xlabel(axis_dict[key])
    
    try:
        start, end = xaxis_delimitter(arr)
        plt.xlim(start - 1, end + 1)
    except:
        pass

    if key in naming_dict.keys():
        key = naming_dict[key]+index

        plt.legend(legend, fontsize = '8')

    if has_plot:
        plt.title(key)
        plt.savefig(f'{path}/{key}.png')
    plt.clf()
    plt.close()

# checking diffrence between dicionaries
def compare_run(name1 : str, name2 : str, longprint : bool = False):
    global primary_dic, secondary_dic
    primary_dic, secondary_dic = savedict(write_run_plot.dump_path(name1)), savedict(write_run_plot.dump_path(name2))
    
    compare_dic = {}
    for orignal_key, orignal_value in primary_dic.items():
        secondary_value = secondary_dic[orignal_key]
        
        if not write_run_plot.blacklist_key(orignal_key):
            try:
                compare_dic[orignal_key] = np.allclose(orignal_value, secondary_value)
            except:
                compare_dic[orignal_key] = 'comparison error'

    val_lis = list(compare_dic.values())
    print(f'comparison of {name1} and {name2}, number of identical arrays: {val_lis.count(True)} number of changed arrays: {val_lis.count(False)} number of comparision errors: {val_lis.count("comparison error")}\n')

    if longprint:
        for key, value in compare_dic.items():
            # theres more options than true and false
            if value != True:
                dic =  write_run_plot.naming_dict
                key, index = write_run_plot.split(key)
                if key in dic.keys():
                    print(dic[key]+index, value)
                else:
                    print(key, value) 

# Check if all vectors in a numpy array are identical.
def are_all_vectors_identical(arr):

    # Check that the array has at least one row
    if arr.shape[0] == 0:
        return False
    
    # Get the first row as a reference vector
    ref_vector = arr[0]
    ref_column = arr[:, 0]

    # Check if all other vectors are equal to the reference vector
    if np.all(np.equal(arr, ref_vector), axis=1).all():
        return 'rows'
    
    elif np.all(np.equal(arr, ref_column.reshape(-1, 1)), axis=0).all():
        return 'columns'
    
    else:
        return True

axis_dict = {
    'ne' : 'nodes',
    'ni' : 'nodes',
    'r' : 'nodes',
    'te' : 'nodes',
    'u' : 'nodes',
    'eav': 'ebins',
    'emis': 'ebins',
    'ev': 'ebins',
    'jnu': 'ebins',
    'kappa': 'ebins',
}


# for plots that include a lot of zeros we essentially zoom on the x axis using the delimitters
def xaxis_delimitter(lst):
    ranges = []
    start_idx = None
    for i in range(len(lst)):
        if lst[i] != 0 and start_idx is None:
            # Start of a new range
            start_idx = i
        elif lst[i] == 0 and start_idx is not None:
            # End of the current range
            ranges.append((start_idx, i-1))
            start_idx = None
    if start_idx is not None:
        # End of the list is also end of the last range
        ranges.append((start_idx, len(lst)-1))

    start = ranges[0][0]
    end = ranges[-1][-1]

    return start, end

# for plotting .plt files created by cretin
def plt_files(path: str, trials : list):
    all_extract_dict  = {}
    for trial in trials:

        p = f'{paths.to_personal_data()}{trial}/{trial}.plt'
        if os.path.exists(p):
            data = plt_file.create_plot(trial, multiplot= True)

            for key, value in data.items():
                value = np.array(value)
                value = value.astype('float')
                X = value.T[0]
                Y = value.T[1]
                newkey = (trial,*key)
                all_extract_dict[newkey] = [X,Y]


    if len(all_extract_dict) > 0:
        unique_keys = set(key[1:] for key in all_extract_dict.keys())

        for unq_key in unique_keys:
            legend = []
            for key, value in all_extract_dict.items():
                if key[1:] == unq_key:
                    legend.append(key[0])
                    [X,Y] = value
                    title = key[2:]
                    xlabel, ylable, goto = key[2], key[3], f'{path}/{title}.png' 
                    plt.plot(X,Y)

            plt.legend(legend)
            plt.title(title)
            plt.xlabel(xlabel)  
            plt.ylabel(ylable)  
            plt.savefig(goto)
            plt.clf()
            plt.close()