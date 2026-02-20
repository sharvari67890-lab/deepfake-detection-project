import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.callbacks import EarlyStopping
import os

DATASET_PATH = "dataset/image_dataset"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_HEAD = 8
EPOCHS_FINE = 5

# ----------------------------
# Load Dataset
# ----------------------------
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_PATH,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.map(lambda x, y: (preprocess_input(x), y)).prefetch(AUTOTUNE)
val_ds = val_ds.map(lambda x, y: (preprocess_input(x), y)).prefetch(AUTOTUNE)

# ----------------------------
# Build Model
# ----------------------------
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# ----------------------------
# Train Head
# ----------------------------
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_HEAD
)

# ----------------------------
# Fine-Tune Last 20 Layers
# ----------------------------
base_model.trainable = True

for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_FINE
)

# ----------------------------
# Final Evaluation
# ----------------------------
loss, accuracy = model.evaluate(val_ds)
print("FINAL Validation Accuracy:", accuracy)

# ----------------------------
# Save
# ----------------------------
os.makedirs("models", exist_ok=True)
model.save("models/image_model.h5")

print("Training complete. Model saved.")
    