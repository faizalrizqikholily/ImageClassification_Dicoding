# -*- coding: utf-8 -*-
"""Image_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Qu6GZKCcXYZLkD000mGf82SM1h8MUkMq

*   Nama : Faizal Rizqi Kholily
*   Dicoding : faizalrizqikholily
*   Linked in : www.linkedin.com/in/faizalrizqikholily
*   Github : www.github.com/faizalrizqikholily

## 1. Install dan Import Library yang akan digunakan
"""

# Install library yang diperlukan
!pip install split-folders

import zipfile
import os
import splitfolders
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import shutil
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from google.colab import files
from IPython.display import Image
import numpy as np

"""## 2.Mengunduh dan Mengekstrak Dataset"""

!wget https://github.com/dicodingacademy/assets/releases/download/release/rockpaperscissors.zip


with zipfile.ZipFile('rockpaperscissors.zip', 'r') as zip_ref:
    zip_ref.extractall('datacuy')

"""Kode ini digunakan untuk mengunduh dataset rockpaperscissors.zip dari URL yang diberikan dan mengekstraknya ke dalam direktori "dataset".

## 3. Membagi Dataset menjadi Train dan Validation Set
"""

input_folder = 'datacuy/rockpaperscissors'
output_folder = 'dataset_split'


splitfolders.ratio(input_folder, output=output_folder, seed=42, ratio=(0.6, 0.4), group_prefix=None)


folder_to_delete1 = 'dataset_split/train/rps-cv-images'
shutil.rmtree(folder_to_delete1, ignore_errors=True)


folder_to_delete2 = 'dataset_split/val/rps-cv-images'
shutil.rmtree(folder_to_delete2, ignore_errors=True)

"""Kode ini membagi dataset menjadi train set dan validation set dengan proporsi 60% train dan 40% validation. File disalin ke direktori yang sesuai.

## 4. Augmentasi Gambar dan Pembuatan Model
"""

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

validation_datagen = ImageDataGenerator(rescale=1./255)


train_generator = train_datagen.flow_from_directory(
    'dataset_split/train',
    target_size=(150, 150),
    batch_size=32,
    class_mode='sparse'
)

validation_generator = validation_datagen.flow_from_directory(
    'dataset_split/val',
    target_size=(150, 150),
    batch_size=32,
    class_mode='sparse'
)

model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(512, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

"""Kode ini mengatur augmentasi gambar menggunakan ImageDataGenerator, membuat model Sequential dengan arsitektur CNN sederhana, dan mengompilasi model.

## 5. Melatih Model
"""

# Callback untuk menghentikan pelatihan jika akurasi di atas 97%
class CustomCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        if logs.get('accuracy') > 0.97:
            print("\nAkurasi di atas 97%. Pelatihan dihentikan.")
            self.model.stop_training = True

# Callback untuk menyimpan model terbaik berdasarkan val_acc
model_checkpoint = ModelCheckpoint('best_model.h5', monitor='val_accuracy', save_best_only=True)

# Callback untuk menghentikan pelatihan jika akurasi di atas 97%
custom_callback = CustomCallback()

# Melatih model dengan data augmented
history = model.fit(
    train_generator,
    steps_per_epoch=len(train_generator),
    epochs=40,
    validation_data=validation_generator,
    validation_steps=len(validation_generator),
    callbacks=[model_checkpoint, custom_callback]
)

# Menyimpan model terakhir
model.save('rock_paper_scissors_model_final.h5')

"""Kode ini melatih model menggunakan data yang telah di-augmentasi dan menyimpan model terbaik.

## 6. Visualisasi Hasil Model
"""

# Plot akurasi training dan validation
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Plot loss training dan validation
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

"""## 7. Memprediksi Gambar yang Diunggah"""

# Fungsi untuk memprediksi gambar yang diunggah
def predict_uploaded_image(model, img_path):
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Tambahkan dimensi batch

    prediction = model.predict(img_array)
    class_index = np.argmax(prediction)
    classes = ['paper', 'rock', 'scissors']

    # Menampilkan gambar
    plt.imshow(img)
    plt.axis('off')
    plt.show()

    print(f'Predicted class: {classes[class_index]}')
    print(f'Prediction probabilities: {prediction[0]}')

"""Kode ini mendefinisikan fungsi predict_uploaded_image yang digunakan untuk memprediksi kelas gambar yang diunggah setelah melatih model. Fungsi ini menggunakan model yang telah dilatih sebelumnya dan mengunggah gambar untuk diprediksi."""

# Mengunggah gambar
uploaded = files.upload()

# Mengambil path dari gambar yang diunggah
uploaded_image_path = next(iter(uploaded))

# Memprediksi gambar yang diunggah
predict_uploaded_image(model, uploaded_image_path)