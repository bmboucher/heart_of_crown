import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from .state import STATE_SIZE
from .action import ACTION_SIZE

inputs = keras.Input(shape=(STATE_SIZE+ACTION_SIZE,))

x = inputs
for _ in range(3):
    dense = layers.Dense((STATE_SIZE + ACTION_SIZE) // 2, activation='relu')
    x = dense(x)
collapse = layers.Dense(1, activation='relu')
model = keras.Model(inputs=inputs, outputs=collapse(x), name='hoc_model')
print(model.summary())