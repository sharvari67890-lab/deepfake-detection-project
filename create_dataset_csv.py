import os
import pandas as pd

base_path = "dataset/image_dataset"

real_path = os.path.join(base_path, "real")
fake_path = os.path.join(base_path, "fake")

data = []

for img in os.listdir(real_path):
    data.append([os.path.join(real_path, img), 0])

for img in os.listdir(fake_path):
    data.append([os.path.join(fake_path, img), 1])

df = pd.DataFrame(data, columns=["image_path", "label"])
df.to_csv("dataset/image_dataset.csv", index=False)

print("CSV dataset created successfully!")
