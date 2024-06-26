# for running the premades .gen files in the test folder paths.to_previous_experiments()
import os
import paths
import write_run_plot

def run(sub_name:str = None, path:str = paths.to_previous_experiments()):
    
    exception_triggered = True  # Initialize the flag variable

    for file_name in os.listdir(path):
        if sub_name in file_name:
            write_run_plot.run(file_name, longprint = False, newpath = path)
            write_run_plot.plot_dump(file_name, longprint = False, plot_duplicates = False, newpath = path)
            exception_triggered = False  # Set the flag to False if the if statement triggered

    if exception_triggered:
        raise Exception('name not present in any files in test folder')