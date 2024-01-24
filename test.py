import generator_object, write_run_plot, serial_sim_tools, animate, plt_file, to_generator_string, paths, json


from importlib import reload
for obj in [generator_object, to_generator_string, write_run_plot, serial_sim_tools, animate, plt_file]:
    reload(obj)


def switches(**kwargs):
    with open(f"{paths.to_folder_cretin()}/switch_mappings.json", 'r') as file:
        options = json.load(file)

    for key, value in kwargs.items():
        for dict_key, dict_value in options.items():
            if key in dict_key:
                print(key ,value, dict_key, dict_value)



import json
import paths  # Assuming 'paths' is a module you have for path handling

def switches():
    with open(f"{paths.to_folder_cretin()}/switch_mappings.json", 'r') as file:
        options = json.load(file)['main']
        lis = []
        for key in options.keys():
            arg = '_'.join(key.split('_')[1:])
            lis.append(f'{arg}:str = None')

    func_def = f"""
def func({', '.join(lis)}):
    print("hello")
    """
    return func_def

# Executing the dynamically created function definition
exec(switches())

# Execute the function definition
#exec(switches())

# Now you can call func() with the parameters
#print(func(include_degeneracy="no degeneracy"))
