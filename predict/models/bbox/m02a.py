import numpy as np
from keras.models import Model
from keras.layers import Flatten, Dense, Input, merge
from keras.layers import Convolution2D, MaxPooling2D, BatchNormalization, Activation, AveragePooling2D


def res_block(input_tensor, nb_filters=16, block=0, subsample_factor=1):
    subsample = (subsample_factor, subsample_factor)

    x = BatchNormalization(axis=3)(input_tensor)
    x = Activation('relu')(x)
    x = Convolution2D(nb_filters, 3, 3, subsample=subsample, border_mode='same')(x)
    x = BatchNormalization(axis=3)(x)
    x = Activation('relu')(x)
    x = Convolution2D(nb_filters, 3, 3, subsample=(1, 1), border_mode='same')(x)

    if subsample_factor > 1:
        shortcut = Convolution2D(nb_filters, 1, 1, subsample=subsample, border_mode='same')(input_tensor)
    else:
        shortcut = input_tensor

    x = merge([x, shortcut], mode='sum')
    return x


def define_model():
    img_input = Input(shape=(32, 32, 1))

    x = Convolution2D(32, 3, 3, subsample=(1, 1), border_mode='same')(img_input)

    x = res_block(x, nb_filters=32, block=0, subsample_factor=1)
    x = res_block(x, nb_filters=32, block=0, subsample_factor=1)
    x = res_block(x, nb_filters=32, block=0, subsample_factor=1)

    x = res_block(x, nb_filters=64, block=1, subsample_factor=2)
    x = res_block(x, nb_filters=64, block=1, subsample_factor=1)
    x = res_block(x, nb_filters=64, block=1, subsample_factor=1)

    x = res_block(x, nb_filters=128, block=2, subsample_factor=2)
    x = res_block(x, nb_filters=128, block=2, subsample_factor=1)
    x = res_block(x, nb_filters=128, block=2, subsample_factor=1)
    x = res_block(x, nb_filters=128, block=2, subsample_factor=1)

    x = res_block(x, nb_filters=256, block=3, subsample_factor=2)
    x = res_block(x, nb_filters=256, block=3, subsample_factor=1)
    x = res_block(x, nb_filters=256, block=3, subsample_factor=1)
    x = res_block(x, nb_filters=256, block=3, subsample_factor=1)

    x = BatchNormalization(axis=3)(x)
    x = Activation('relu')(x)

    x = AveragePooling2D(pool_size=(3, 3), strides=(2, 2), border_mode='valid')(x)
    x = Flatten()(x)

    bbox = Dense(4, activation='linear', name='bbox')(x)
    model_bbox = Model(img_input, bbox)
    model_bbox.compile(optimizer='adam', loss='mae')

    return model_bbox
