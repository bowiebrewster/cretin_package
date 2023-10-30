# this cute little tool for manaing all the paths
import os 


def to_path(paths:list, name:str):
    for path in paths:
        if not path.endswith('/'):
            path += '/'

        if os.path.exists(path):
            return path
        
    raise Exception(f'none of the paths provided in {name} exist in this system')


def to_personal_data():
    paths = ['/home/brewster/Desktop/cretin_package-master/Personal_experiments/']
    return to_path(paths, 'to_personal_data')

def to_folder_cretin():
    paths = ['/home/brewster/Desktop/cretin_package-master/']
    return to_path(paths, 'to_folder_cretin')

def to_previous_experiments():
    paths = ['/home/brewster/Desktop/cretin_package-master/Premade_cretin_tests/']
    return to_path(paths, 'to_previous_experiments')

def to_cretin_ex():
    paths = [f"{os.environ['HOME']}/Desktop/cretin.v2_19_test/bin"]
    return to_path(paths, 'to_cretin_ex')
