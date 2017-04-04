import pickle as pkl
from matplotlib.image import imread
from skimage.color import rgb2gray
import glob
import os
import numpy as np
import sys
from lasagne.layers import DenseLayer
from lasagne.layers import InputLayer
from lasagne.layers import DropoutLayer
from lasagne.layers import Conv2DLayer
from lasagne.layers import MaxPool2DLayer
from lasagne.nonlinearities import softmax
from lasagne.updates import adam
from lasagne.layers import get_all_params
from nolearn.lasagne import NeuralNet
from nolearn.lasagne import TrainSplit
from nolearn.lasagne import objective
from nolearn.lasagne import PrintLayerInfo


def load_roi_images(path_to_samples_dir, normalize = False, convert2gray = False):
    """
    Modified from:
    http://nbviewer.ipython.org/github/dnouri/nolearn/blob/master/docs/notebooks/CNN_tutorial.ipynb#
    """
    X = []
    y = []
    pos_paths = glob.glob(os.path.join(path_to_samples_dir,'positive_samples/*.png'))
    neg_paths = glob.glob(os.path.join(path_to_samples_dir,'negative_samples/*.png'))

    for posneg in [pos_paths, neg_paths]:
        for img_path in posneg:
            img = imread(img_path)
            if convert2gray:
                img = rgb2gray(img)

            X.append(img)
            y.append(1 if 'positive' in img_path else 0)

    # Theano works with fp32 precision
    X = np.array(X).astype(np.float32)
    y = np.array(y).astype(np.int32)

    #drop alpha channel if exists (generally always = 1)
    if (len(np.shape(X)) == 4) and (np.shape(X)[-1] == 4):
        X = X[:,:,:,:3]  #dims: num_samps, pix_x, pix_y, rgb(a)

    if normalize:
        X -= X.mean()
        X /= X.std()


    numcolors = 1 if convert2gray else 3
    print np.shape(X)

    # For convolutional layers, the default shape of data is bc01,
    # i.e. batch size x color channels x image dimension 1 x image dimension 2.
    # Therefore, we reshape the X data to -1, 1, 28, 28.
    X = X.reshape(
        -1,  # number of samples, -1 makes it so that this number is determined automatically
        numcolors,   # 3 color channel or 1 for grays, 
        28,  # first image dimension (vertical)
        28,  # second image dimension (horizontal)
    )

    return X, y



if __name__ == '__main__':

    X, y = load_roi_images('path/to/roi/directories', normalize=True, convert2gray=False)
    
    #copied from layers4 definition in
    #https://github.com/dnouri/nolearn/blob/master/docs/notebooks/CNN_tutorial.ipynb
    poollayers1 = [
    (InputLayer, {'shape': (None, X.shape[1], X.shape[2], X.shape[3])}),

    (Conv2DLayer, {'num_filters': 32, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 32, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 32, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 32, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 32, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 32, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 32, 'filter_size': (3, 3), 'pad': 1}),
    (MaxPool2DLayer, {'pool_size': (2, 2)}),

    (Conv2DLayer, {'num_filters': 64, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 64, 'filter_size': (3, 3), 'pad': 1}),
    (Conv2DLayer, {'num_filters': 64, 'filter_size': (3, 3), 'pad': 1}),
    (MaxPool2DLayer, {'pool_size': (2, 2)}),

    (DenseLayer, {'num_units': 64}),
    (DropoutLayer, {}),
    (DenseLayer, {'num_units': 64}),

    (DenseLayer, {'num_units': 2, 'nonlinearity': softmax}),

    ]

    layer_info = PrintLayerInfo()


    poolnet = NeuralNet(layers=poollayers1, max_epochs=400, update=adam,
                    update_learning_rate=0.0002, verbose=2,
                    train_split=TrainSplit(eval_size=0.25))

    poolnet.fit(X, y)

    
    #upping recursion depth (sorta arbitrarily to 10k) to avoid pickling error
    sys.setrecursionlimit(10000)
    pkl.dump(poolnet, open('poolnet.pkl','wb'))

