# -*- coding: utf-8 -*-
"""ImageClassification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18ZqBSd-VeAwtt7FU4fPjPBtsp1yBryb5
"""

!pip install -q kaggle

from google.colab import files

files.upload()

! mkdir ~/.kaggle

! cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

# import data dari kaggle
!kaggle datasets download -d anbumalar1991/fight-dataset

import zipfile,os

# ekstrak dataset
local_zip = '/content/fight-dataset.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

base_dir = '/content/actions (2)/actions/train'

!pip install split-folders

import splitfolders

# membagi data training dan data testing
splitfolders.ratio(base_dir, output=base_dir, ratio=(0.8,0.2))

train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'val')

os.listdir(train_dir)

# membuat direktori label pada direktori data training
train_kick_dir = os.path.join(train_dir, 'kick')
train_stand_dir = os.path.join(train_dir, 'stand')
train_wave_dir = os.path.join(train_dir, 'wave')
train_ride_horse_dir = os.path.join(train_dir, 'ride_horse')
train_shoot_gun_dir = os.path.join(train_dir, 'shoot_gun')
train_push_dir = os.path.join(train_dir, 'push')
train_punch_dir = os.path.join(train_dir, 'punch')
train_hit_dir = os.path.join(train_dir, 'hit')

# membuat direktori label pada direktori data validasi
validation_kick_dir = os.path.join(validation_dir, 'kick')
validation_stand_dir = os.path.join(validation_dir, 'stand')
validation_wave_dir = os.path.join(validation_dir, 'wave')
validation_ride_horse_dir = os.path.join(validation_dir, 'ride_horse')
validation_shoot_gun_dir = os.path.join(validation_dir, 'shoot_gun')
validation_push_dir = os.path.join(validation_dir, 'push')
validation_punch_dir = os.path.join(validation_dir, 'punch')
validation_hit_dir = os.path.join(validation_dir, 'hit')

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    shear_range = 0.2,
                    fill_mode = 'nearest'
                    )

test_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    shear_range = 0.2,
                    fill_mode = 'nearest'
                    )

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(150,150),
    color_mode = "rgb",
    batch_size= 128,
    shuffle = True,
    class_mode='categorical'
)

validation_generator = test_datagen.flow_from_directory(
        validation_dir,
        target_size=(150, 150),
        color_mode = "rgb",
        batch_size=128,
        shuffle = False,
        class_mode='categorical'
        )

# pemodelan sequential dengan menerapkan Conv2D Maxpooling Layer
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), padding='same', activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3,3), padding='same', activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), padding='same', activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(8, activation='softmax')
])

from tensorflow.keras.optimizers import Adam

# compile model dengan 'adam' optimizer loss function 'categorical_crossentropy' dengan learning rate 0.00146
Adam(learning_rate=0.00146, name='Adam')
model.compile(loss='categorical_crossentropy',
              optimizer=tf.optimizers.Adam(),
              metrics=['accuracy'])

class myCallback(tf.keras.callbacks.Callback): 
    def on_epoch_end(self, epoch, logs={}): 
        if(logs.get('accuracy') > 0.92 and logs.get('val_accuracy') > 0.92):
            print("\nReached 92% accuracy") 
            self.model.stop_training = True 
     
callbacks = myCallback()

history = model.fit(
      train_generator,
      steps_per_epoch=425,
      epochs=100,
      validation_data=validation_generator,
      validation_steps=106,
      verbose=2,
      callbacks=[callbacks]
      )

import matplotlib.pyplot as plt

# membuat plot loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# membuat plot akurasi
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Akurasi Model')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

import warnings

# menghilangkan warning
warnings.filterwarnings('ignore')

# convert model
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# save model
with open('RPS_model.tflite', 'wb') as f:
  f.write(tflite_model)