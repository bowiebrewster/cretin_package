# this cute little tool for manaing all the paths
import os 

def to_personal_data():
    #add the path to your personal folder here, this is where by defualt all you generator files will be written too and the correspoding plots will be send to 
    path_test = '/home/brewster/Desktop/cretin_main/Personal_experiments/'

    if os.path.exists(path_test): 
        path = path_test 

    else:
        raise Exception("add your path to the 'to_personal_data' in paths.py")
    
    if not path.endswith('/'):
        path += '/'

    return path

def to_folder_cretin():
    #add the path to the folder where this file is located. 
    path_test = '/home/brewster/Desktop/cretin_main/Code/'

    if os.path.exists(path_test): 
        path = path_test 

    else:
        raise Exception("add your path to the 'to_folder_cretin' in paths.py")
    
    if not path.endswith('/'):
        path += '/'

    return path


def to_previous_experiments():
    #add the path to your test folder here, the "test" folder contains the premade generator files and will contain 
    # the output of the simulation (ie log files and plots)
    path_test = '/home/brewster/Desktop/cretin_main/Premade_cretin_tests/'

    if os.path.exists(path_test): 
        path = path_test 

    else:
        raise Exception("add your path to the 'to_previous_experiments' in paths.py")

    if not path.endswith('/'):
        path += '/'

    return path

def to_cretin_ex():

    #there is where the backend cretin is located that will do our simulations  
    path_cretin_ex = f"{os.environ['HOME']}/Desktop/cretin.v2_19_test/bin"

    if os.path.exists(path_cretin_ex): 
        path = path_cretin_ex 

    else:
        raise Exception("add your path to the 'to_cretin_ex' in paths.py")

    return path