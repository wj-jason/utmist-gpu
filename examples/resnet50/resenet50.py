import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
import numpy as np

def ResNet50_multi_label(pretrained=True, num_classes=36, input_shape=(224,224,3)):
  weights = 'imagenet' if pretrained else None
  base_model = ResNet50(weights=weights, include_top=False, input_tensor=Input(shape=input_shape))

  x = base_model.output
  x = GlobalAveragePooling2D()(x)
  output_tensor = Dense(num_classes, activation='sigmoid')(x)

  model = Model(inputs=base_model.input, outputs=output_tensor)
  return model

def preprocess_spectrograms_for_resnet50(spectrograms):
    # Converts spectrograms to shape (224, 224, 3)
    preprocessed = []
    for spec in spectrograms:
        spec = tf.expand_dims(spec, -1)  # Add channel dimension (128, 646, 1)
        spec_resized = tf.image.resize(spec, (224, 224))  # Now it has 3 dimensions
        spec_resized = tf.image.grayscale_to_rgb(spec_resized)  # Convert to 3 channels (224, 224, 3)
        preprocessed.append(spec_resized)
    return np.array(preprocessed)
