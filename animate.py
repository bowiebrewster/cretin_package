# This file is for turning many plots into an animation. Inspired by seeing 50 time slices from serial sim tools.
# the data from the plots should be 2*N (X vector and Y vector) *M (Time slices)

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os, h5py, glob, shutil, matplotlib, paths

matplotlib.rcParams['animation.ffmpeg_path'] = paths.to_animation()


def ex(data, path:str, name:str):
    if type(data) != type(np.array([])):
        raise Exception('data type must be nump array')

    if len(data.shape) != 3 or data.shape[0] != 2:
        raise Exception('Data must be shape (2, N, M)') 

    def update_frame(i):
        ax.clear()
        if i < M:
            ax.clear()
            x = data[0, :, i]  # Assuming your data is a 2*N*M matrix
            y = data[1, :, i]  # Assuming your data is a 2*N*M matrix
            ax.plot(x, y)
            ax.set_title(f'Frame {i}')

    # Create a figure and axis for the animation
    fig, ax = plt.subplots()

    # Assuming your data is a 2*N*M matrix
    M = data.shape[2]
    
    # Create an animation object
    ani = animation.FuncAnimation(fig, update_frame, frames = M, repeat=False)

    # Save the animation as a video (you can change the format and bitrate as needed)
    ani.save('output_animation.mp4', writer='ffmpeg', bitrate=1800)



# rewriting plot from serial sim tools


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
        path = path_test + name + '/video'
        if os.path.exists(path):
            shutil.rmtree(path) 
        os.mkdir(path)
        

        keys = [key for key in f.keys() if name in key]

        for key in f.keys():
            arr = np.array(f[key])

            


# testing functionality
"""
def z(x ,y):
    return np.sin(x)+np.cos(y)**2


def test_data(M, N):
    N = 100

    # Number of time steps
    M = 100

    # Create a time vector
    t = np.linspace(0, 1, M)

    # Create an empty data array to store x and y values
    data = np.zeros((2, M, N))

    # Generate the data
    for i in range(M):
        exponent = 0.5 + (i / (M - 1)) * 1.5  # Increase the exponent gradually
        x = np.linspace(0.1, 10, N)
        y = x ** exponent

        # Store x and y values in the data array
        data[0, :, i] = x
        data[1, :, i] = y

    return data

data = test_data(100, 100)
print(data.shape)

def check_time_frame(data):
    x_vec_50 = data[0, :, 50]
    y_vec_50 = data[1, :, 50]
    plt.plot(x_vec_50,y_vec_50)
    plt.show()

"""