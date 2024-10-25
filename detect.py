from flask import Flask, request, jsonify, render_template
import joblib
from datetime import datetime
from scapy.all import *
import os
import numpy as np
import pandas as pd
from collections import deque

app = Flask(__name__)

model = joblib.load("rssi_model.pkl")

# Buffer to store the last 15 RSSI readings
rssi_buffer_15 = deque(maxlen=15)
# Buffer to store the last 45 RSSI readings for most probable status
rssi_buffer_45 = deque(maxlen=45)

# Initialize previous status for logging
previous_status_most_probable = None

# Check if the interface environment variable is set
if 'NETWORK_INTERFACE' not in os.environ:
    # Ask the user for the network interface to monitor
    interface = input("Enter the network interface to monitor (e.g., 'wlxf0a7319fdcaa'): ")
    # Set the environment variable for future use
    os.environ['NETWORK_INTERFACE'] = interface
else:
    # Use the existing environment variable
    interface = os.environ['NETWORK_INTERFACE']

# Function to collect real-time RSSI data
def collect_real_rssi_data(interface=interface, num_samples=1):
    rssi_values = []
    
    def packet_handler(packet):
        if packet.haslayer(Dot11):
            if hasattr(packet, 'dBm_AntSignal'):
                rssi_values.append(packet.dBm_AntSignal)
        return len(rssi_values) >= num_samples

    sniff(iface=interface, prn=packet_handler, store=0, count=num_samples)
    if len(rssi_values) > 0:
        return rssi_values
    return None

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/predict", methods=["POST"])
def predict():
    global previous_status_most_probable
    print("Collecting real-time RSSI data")
    # Collect real-time RSSI data
    rssi_values = collect_real_rssi_data()
    
    if rssi_values is None:
        print("Failed to collect RSSI data")
        return jsonify({"error": "Failed to collect RSSI data"}), 500

    print(f"Collected RSSI values: {rssi_values}")

    # Add the new RSSI values to the buffers
    rssi_buffer_15.extend(rssi_values)
    rssi_buffer_45.extend(rssi_values)

    # Initialize the status
    status_live = "Unknown"
    status_avg = "Unknown"
    status_most_probable = "Unknown"

    # Calculate the live status
    live_rssi = rssi_values[-1]
    live_features = [live_rssi, 0, live_rssi, live_rssi]  # std_rssi, min_rssi, max_rssi are not meaningful for a single value
    live_features_df = pd.DataFrame([live_features], columns=["rssi", "std_rssi", "min_rssi", "max_rssi"])
    live_prediction = model.predict(live_features_df)
    status_live = "Occupied" if live_prediction[0] == 1 else "Empty"

    # Calculate the average status for the last 15 readings
    avg_rssi_15, avg_features_df_15 = None, None
    if len(rssi_buffer_15) >= 15:
        avg_rssi_15 = np.mean(list(rssi_buffer_15))
        std_rssi_15 = np.std(list(rssi_buffer_15))
        min_rssi_15 = np.min(list(rssi_buffer_15))
        max_rssi_15 = np.max(list(rssi_buffer_15))
        
        avg_features_15 = [avg_rssi_15, std_rssi_15, min_rssi_15, max_rssi_15]
        avg_features_df_15 = pd.DataFrame([avg_features_15], columns=["rssi", "std_rssi", "min_rssi", "max_rssi"])
        
        avg_prediction_15 = model.predict(avg_features_df_15)
        status_avg = "Occupied" if avg_prediction_15[0] == 1 else "Empty"

        print(f"Last 15 RSSI values: {list(rssi_buffer_15)}")
        print(f"Average RSSI: {avg_rssi_15}, Std RSSI: {std_rssi_15}, Min RSSI: {min_rssi_15}, Max RSSI: {max_rssi_15}")
        print(f"Average Status: {status_avg}")

    # Calculate the most probable status for the last 45 readings
    avg_rssi_45, avg_features_df_45 = None, None
    if len(rssi_buffer_45) >= 45:
        avg_rssi_45 = np.mean(list(rssi_buffer_45))
        std_rssi_45 = np.std(list(rssi_buffer_45))
        min_rssi_45 = np.min(list(rssi_buffer_45))
        max_rssi_45 = np.max(list(rssi_buffer_45))
        
        avg_features_45 = [avg_rssi_45, std_rssi_45, min_rssi_45, max_rssi_45]
        avg_features_df_45 = pd.DataFrame([avg_features_45], columns=["rssi", "std_rssi", "min_rssi", "max_rssi"])
        
        avg_prediction_45 = model.predict(avg_features_df_45)
        status_most_probable = "Occupied" if avg_prediction_45[0] == 1 else "Empty"

        most_probable_status = "The room is most probably " + status_most_probable.lower()

        print(f"Last 45 RSSI values: {list(rssi_buffer_45)}")
        print(f"Most Probable Status: {status_most_probable}")

        # Log the initial status and subsequent changes
        if previous_status_most_probable is None:
            previous_status_most_probable = status_most_probable
            with open('wisen.log', 'a') as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Initial Most Probable Status set to {status_most_probable}\n")
        elif status_most_probable != previous_status_most_probable:
            with open('wisen.log', 'a') as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Most Probable Status changed to {status_most_probable}\n")
            previous_status_most_probable = status_most_probable
    else:
        most_probable_status = "Not enough data to determine room status"

    response = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "live_rssi": float(live_rssi),
        "average_rssi_15": avg_rssi_15 if len(rssi_buffer_15) >= 15 else None,
        "status_live": status_live,
        "status_avg": status_avg,
        "most_probable_status": most_probable_status
    }
    
    print(f"Response: {response}")
    return jsonify(response)

if __name__ == "__main__":
    # Ensure the script is run as root
    if os.geteuid() != 0:
        print("This script must be run as root.")
        exit(1)

    # Log the initial start of the application
    with open('wisen.log', 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Application started successfully.\n")
    
    app.run(debug=True, host='127.0.0.1')
