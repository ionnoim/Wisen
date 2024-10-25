import signal
from scapy.all import *
import datetime

# Ask the user for the network interface to monitor
interface = input("Enter the network interface to monitor (e.g., 'wlxf0a7319fdcaa'): ")

# Open a file to log RSSI values with buffering enabled
log_file = open("rssi_log.txt", "w", buffering=1)

# Function to process packets
def packet_handler(packet):
    print("Packet received")  # Debug statement
    if packet.haslayer(Dot11):
        print("Packet has Dot11 layer")  # Debug statement
        # Extract RSSI if available
        rssi = packet.dBm_AntSignal if hasattr(packet, 'dBm_AntSignal') else None
        if rssi is not None:
            # Log RSSI with a timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp}, {rssi}\n"
            log_file.write(log_entry)
            print(f"{timestamp} - RSSI: {rssi} dBm")
        else:
            print("RSSI field not found in packet")  # Debug statement
    else:
        print("Packet does not have Dot11 layer")  # Debug statement

# Function to stop packet sniffing
def stop_sniffing(signum, frame):
    print("\nSniffing stopped by user")
    log_file.close()
    exit(0)

# Register the signal handler for SIGINT
signal.signal(signal.SIGINT, stop_sniffing)

print(f"Starting packet sniffing on interface '{interface}'. Press Ctrl+C to stop.")

# Sniff packets from the user-provided WiFi interface
try:
    sniff(iface=interface, prn=packet_handler, store=0, monitor=True)
except Exception as e:
    print(f"Error occurred: {e}")
    log_file.close()
