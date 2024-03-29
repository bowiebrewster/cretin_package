import os
import glob
import matplotlib.pyplot as plt
import matplotlib
import paths
from matplotlib import animation
from matplotlib.animation import FuncAnimation

# this file is for animating the space time plots to turn them into videos of regular plots instead of heatmaps

matplotlib.rcParams['animation.ffmpeg_path'] = paths.to_animation()
def ex(image_dir : str, images_name:str):

    # Define the path to the directory containing the images

    # Get a list of image file paths in the directory
    image_files = sorted(glob.glob(os.path.join(image_dir, f'{images_name}*.png')))

    # Create a function to update the frames
    def update_frame(i):
        # Load the image for the current frame
        img = plt.imread(image_files[i])
        # Display the image on the figurew
        im.set_array(img)
        return im,

    # Create a figure and axis
    fig, ax = plt.subplots()
    ax.axis('off')  # Turn off the axis and ticks

    # Load the first image and display it
    img = plt.imread(image_files[0])
    im = ax.imshow(img)

    # Create the animation
    ani = animation.FuncAnimation(fig, update_frame, frames=len(image_files), repeat=False)

    # Save the animation as a video
    ani.save(f'{image_dir}/{images_name}.mp4', writer='ffmpeg')  # You need to have ffmpeg installed

    print(f'animation saved at {image_dir}')


def ex_heatmap(df, path, xvar1, yvar, title) :

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)

    # Set the x-axis to match the column names (positions)
    try:
        positions = df.columns.astype(float)
    except:
        df.columns = df.columns.get_level_values(1)
        positions = df.columns.astype(float)

    def init():
        y_min = df.values.min()
        y_max = df.values.max()
        if abs(y_min - y_max) < 1.e-4:
            y_min, y_max = (y_min - 1)*.99, (y_max + 1)*1.01  # Adjust these values as appropriate for your data

        ax.set_xlim(positions.min(), positions.max())
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(xvar1)
        ax.set_ylabel(yvar)
        ax.set_title(title)
        return line,

    # Update function for each frame
    def update(frame):
        line.set_data(positions, df.iloc[frame])
        return line,

    # Create animation
    ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True)

    # Save the animation
    ani.save(path+'.mp4', writer='ffmpeg', fps=20)
    plt.close()
    