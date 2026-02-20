import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# Load model once
model = tf.keras.models.load_model("models/image_model.h5")


def predict_image_model(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    prediction = model.predict(img_array)[0][0]

    print("RAW:", prediction)

    real_score = float(prediction)
    fake_score = float(1 - prediction)

    if real_score > fake_score:
      verdict = "REAL"
    else:
      verdict = "FAKE"

    return verdict, real_score, fake_score
