# Wisen Room Status Monitor

Open-source project by ionnoim.

## Introduction

This project aims to bring awareness of WiFi sensing technology to researchers and enthusiasts. **Wisen** leverages the power of a pre-trained AI model to perform live analysis of RSSI (Received Signal Strength Indicator) data to determine whether a room is probably occupied or vacant.

## Features

- **Live Status Monitoring**: Analyze real-time RSSI data to predict room occupancy.
- **AI-powered Predictions**: AI models trained to provide high-accuracy predictions based on RSSI data.
- **Short-term and Long-term Status Monitoring**: Analyze room status for short-term (1 min) and long-term (4 min) predictions.

## Requirements

To run Wisen, you will need:
- A WiFi interface that supports monitor mode.
- A router is optional if you want to monitor in-line or multi-room.
- Python installed on your machine.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/ionnoim/Wisen
   ```

2. Set up a virtual environment using Python:

   ```bash
   python3 -m venv Wisen-env
   source Wisen-env/bin/activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** To avoid dependency issues, you may need to run scripts with the full path to Python in your virtual environment.
   
## Setup

With router connected for in-line monitoring and multi-room: The ideal setup is a room where the router is on one side and the WiFi interface on the opposite side. The monitored space should be between both devices. It can work in other setups, but performance may vary. I have tested this going through multiple rooms and was still able to get good predictions. Movement in areas in line with the monitored space can also affect the signal. By experimenting with hardware positioning and retraining the AI, I achieved 99% accuracy.

Note that this also works with a wifi adapter in monitor mode that is simply sitting in the room with no connection to a router and it will monitor the surrounding space.

**Note:** If any major changes are made, such as moving furniture, you will need to re-capture data and re-train the AI.

## Data Capture

1. Set your WiFi interface to monitor mode using the provided `monitor.sh` script, or do it manually.

2. Run `capture.py` and input your interface name.

3. Capture data for both an empty room and an occupied room:

   - For an **empty room**, start the capture, leave the room, and let it run for your chosen duration (e.g., 10 minutes for better accuracy).
   - Save the resulting `rssi_log.txt` file as `empty.txt`.
   
   - For an **occupied room**, repeat the process while inside the room. Perform normal activities (e.g., sitting at a desk) without exaggerating movements.
   - Save the resulting `rssi_log.txt` as `inroom.txt`.

## Training the AI Model

To prepare the data and train the model, run:

```bash
python prepntrain.py
```

The script will provide accuracy results after training. If accuracy is below 80%, capture more data or adjust the physical setup.

## Live Detection

**Warning:** This must be run as root and is served as a Flask app on localhost. This is meant for offline use and is not hardened for internet-facing purposes. 

To start live detection, run:

```bash
python detect.py
```

Then, navigate to [http://localhost:5000](http://localhost:5000) in your browser (you can change the hardcoded port in the source code).

**Note:** All status changes are logged to `wisen.log`.

---

Thanks for your interest in my work. ionnoim@proton.me




