# import tensorflow as tf
# import numpy as np
# from tensorflow.keras.models import load_model
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# model = load_model("models/image_model.h5")

# def predict_image(image_path):
#     img = tf.keras.preprocessing.image.load_img(
#         image_path,
#         target_size=(224, 224)
#     )

#     img_array = tf.keras.preprocessing.image.img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0)
#     img_array = preprocess_input(img_array)

#     prediction = model.predict(img_array)[0][0]

#     fake_score = float(prediction)
#     real_score = float(1 - prediction)

#     verdict = "FAKE" if fake_score > 0.5 else "REAL"

#     awareness = "Prediction based on learned facial feature patterns."

#     return verdict, real_score, fake_score, awareness

import os
from predict_image import predict_image_model  # function that predicts image

CSV_FILE = os.path.join("data", "image_results.csv")
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

# ensure CSV exists
if not os.path.exists(CSV_FILE):
    import csv
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename','verdict','real_score','fake_score','awareness'])
        writer.writeheader()


def analyze_image(file_path, filename):
    # Predict using the actual model
    verdict, real_score, fake_score = predict_image_model(file_path)

    # Awareness message
    if verdict.upper() == "FAKE":
        awareness = "Signs of manipulation detected"
    elif verdict.upper() == "REAL":
        awareness = "Looks authentic based on known patterns"
    else:
        awareness = "No data available"

    # Save to CSV
    import csv
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename','verdict','real_score','fake_score','awareness'])
        writer.writerow({
            'filename': filename,
            'verdict': verdict,
            'real_score': real_score,
            'fake_score': fake_score,
            'awareness': awareness
        })

    return {
    'verdict': verdict,
    'real': round(real_score * 100, 2),
    'fake': round(fake_score * 100, 2),
    'awareness': awareness
}
