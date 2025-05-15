import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('/home/sifatullah/My_Files/01_TUTORIALS/2_opencv/03_yolo/scripts/runs/detect/train6/results.csv')

# Extract precision and recall
precision = df['metrics/precision(B)']
recall = df['metrics/recall(B)']
epochs = df.index  # X-axis as epoch index

# Create subplots
fig, (ax1, ax2) = plt.subplots(1,2, figsize=(8, 6), sharex=False)
fig.suptitle('License plate Training Metrics', fontsize=16)

# Plot precision
ax1.plot(epochs, precision, marker='o', color='blue', linewidth=2)
ax1.set_title('Precision')
ax1.set_ylabel('Precision')
ax1.grid(False)

# Plot recall
ax2.plot(epochs, recall, marker='o', color='green', linewidth=2)
ax2.set_title('Recall')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Recall')
ax2.grid(False)

# Layout adjustments
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.show()
