import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import joblib

def read_rssi_data(file_path, label):
    data = []
    with open(file_path, "r") as log_file:
        for line in log_file:
            timestamp, rssi = line.strip().split(", ")
            data.append([timestamp, float(rssi), label])
    return data

# Load data
inroom_data = read_rssi_data("inroom.txt", 1)
empty_data = read_rssi_data("empty.txt", 0)

# Combine the data
data = inroom_data + empty_data

# Create a DataFrame
df = pd.DataFrame(data, columns=["timestamp", "rssi", "label"])

# Feature engineering with a larger rolling window size
window_size = 20  # Increased window size for better variability
df['std_rssi'] = df['rssi'].rolling(window=window_size).std().fillna(0)
df['min_rssi'] = df['rssi'].rolling(window=window_size).min().fillna(df['rssi'])
df['max_rssi'] = df['rssi'].rolling(window=window_size).max().fillna(df['rssi'])

# Save the DataFrame to a CSV file for future use
df.to_csv("rssi_data.csv", index=False)

# Display the DataFrame
print(df.head(20))  # Display first 20 rows for better visibility
print(df.tail(20))  # Display last 20 rows for better visibility

# Features and labels
X = df[["rssi", "std_rssi", "min_rssi", "max_rssi"]]
y = df["label"]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model using Gradient Boosting Classifier
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy}")

# Save the trained model
joblib.dump(model, "rssi_model.pkl")
