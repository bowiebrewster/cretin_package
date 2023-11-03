import os
import glob
import matplotlib.pyplot as plt
import matplotlib
import paths
from matplotlib import animation

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