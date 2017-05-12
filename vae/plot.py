import matplotlib.pyplot as plt
import numpy as np
import os

from moviepy.editor import ImageSequenceClip
from scipy.ndimage import imread


def make_canvas(vae, batch_size, epoch, n=15, bound=2):
    """
    Creates and saves a 'canvas' of images decoded from a grid in the latent space. 
    
    :param vae: instance of VAE which performs decoding
    :param batch_size: little hack to get dimensions right 
    :param epoch: current epoch of training
    :param n: number of points in each dimension of grid
    :param bound: samples from [-bound, bound] in both z1 and z2 direction
    """
    # create grid (could be done once but requires refactoring)
    spaced_z1 = np.linspace(-bound, bound, n)
    spaced_z2 = np.linspace(-bound, bound, n)

    # create and fill canvas
    canvas = np.empty((28 * n, 28 * n))
    for i, z1 in enumerate(spaced_z1):
        for j, z2 in enumerate(spaced_z2):
            img = vae.z2x(np.array([[z1, z2]] * batch_size))
            canvas[(n - i - 1) * 28:(n - i) * 28, j * 28:(j + 1) * 28] = img

    # make figure and save
    plt.figure(figsize=(10, 10))
    plt.imshow(canvas)
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    plt.savefig('../figs/canvas/' + str(epoch + 1000) + '.png')


def make_canvas_gif():
    """
    Creates and saves gif from images generated by make_canvas().
    """
    # read images
    images = [imread('../figs/canvas/' + file)
              for file in sorted(os.listdir(path='../figs/canvas/'))
              if file != '.gitkeep']
    # durations of frames in log time
    durations = list(np.diff(np.log(4 + np.arange(len(images)))))

    # make clip and save as gif
    clip = ImageSequenceClip(images, durations=durations)
    clip.fps = 25
    clip.write_gif('../canvas.gif')


def make_spread(vae, provider, epoch):
    """
    Shows encoding of 5000 test points in the latent space at a given epoch of training.
    
    :param vae: instance of VAE which performs encoding
    :param provider: provider for test data
    :param epoch: current epoch of training
    """
    # encode 500 test samples in batches of 100
    # zs will hold encoded points
    n_test = 5000
    batch_size = 100
    zs = np.zeros((n_test, 2), dtype=np.float32)
    labels = np.zeros(n_test)
    for i in range(int(n_test / batch_size)):
        x, y = provider.test.next_batch(batch_size)
        labels[(100 * i):(100*(i + 1))] = y
        z = vae.x2z(x)
        zs[(100 * i):(100*(i + 1)), :] = z

    # figure out class means in latent space
    indices = np.array([np.where(labels == i)[0] for i in range(10)])
    classes = np.array([zs[index] for index in indices])
    means = np.array([np.mean(c, axis=0) for c in classes])

    # scatter z points
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)
    ax.scatter(zs[:, 0], zs[:, 1], c=labels)

    # annotate means
    for i, mean in enumerate(means):
        ax.annotate(str(i), xy=mean, size=16,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    # annotate epoch
    ax.annotate("Epoch " + str(epoch), xy=(3.1, 4.4), size=25,
                bbox=dict(boxstyle='round', facecolor='white', alpha=1.))

    # plot details
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()

    plt.savefig('../figs/spread/' + str(epoch + 1000) + '.png')


def make_spread_gif():
    """
    Creates and saves gif from images generated by make_spread().
    """
    # read images
    images = [imread('../figs/spread/' + file)
              for file in sorted(os.listdir(path='../figs/spread/'))
              if file != '.gitkeep']

    # make clip and save
    clip = ImageSequenceClip(images, fps=5)
    clip.write_gif('../spread.gif')
