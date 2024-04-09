from datetime import timedelta
import threading
import socket
import time
import hashlib
import hmac
import os
import collections

# Disable SSL warnings
import urllib3

urllib3.disable_warnings()

# Global variables for rate limiting and connection tracking
last_request_time = time.time()
active_connections = set()
lock = threading.Lock()

# Secret key for HMAC
SECRET_KEY = "mysecretkey"

# Fake IP address and VM IP address for IP filtering
fake_ip = '192.168.1.100'
vm_ip = '10.0.2.15'

# Define the log file path
LOG_FILE = os.path.join(os.getcwd(), "networkinfo.log")

class AnomalyDetector:
    def __init__(self, window_size=100, threshold=2.0):
        self.window_size = window_size
        self.threshold = threshold
        self.request_sizes = collections.deque(maxlen=window_size)

    def add_request(self, request_size):
        self.request_sizes.append(request_size)

    def check_anomaly(self, request_size):
        if len(self.request_sizes) < self.window_size:
            return False
        avg_size = sum(self.request_sizes) / len(self.request_sizes)
        return abs(request_size - avg_size) > self.threshold * avg_size

anomaly_detector = AnomalyDetector()

def rate_limiting():
    global last_request_time
    with lock:
        current_time = time.time()
        time_since_last_request = current_time - last_request_time
        if time_since_last_request < 1:
            time.sleep(1 - time_since_last_request)
        last_request_time = time.time()

def ip_filtering(ip_address, block_for_testing):
    if block_for_testing and ip_address == vm_ip:
        print(f"\nSimulating blocking IP address: {ip_address}")
        return True

def verify_hmac_sha1(request):
    # Generate the base string
    base_string = generate_signature_base_string(request)
    # Calculate the HMAC-SHA1 signature
    sig = hmac_sha1_signature(base_string, request.client_secret, request.token_secret)
    # Compare the calculated signature with the request's signature
    return hmac.compare_digest(sig, request.signature)

def generate_signature_base_string(request):
    method = request.method.upper()  # HTTP method
    url = request.url  # URL of the request
    parameters = "&".join([f"{key}={value}" for key, value in request.args.items()])  # Query parameters
    base_string = f"{method}&{url}&{parameters}"
    return base_string

def hmac_sha1_signature(base_string, client_secret, token_secret):
    key = f"{client_secret}&{token_secret}".encode('utf-8')
    message = base_string.encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha1)
    return signature.hexdigest()

def ping():
    try:
        socket.setdefaulttimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "8.8.8.8"  # Google's DNS server
        port = 53
        server_address = (host, port)
        s.connect(server_address)
    except OSError:
        return False
    else:
        s.close()
        return True

def calculate_time(start, stop):
    difference = stop - start
    seconds = float(str(difference.total_seconds()))
    return str(timedelta(seconds=seconds)).split(".")[0]

def connection_tracking():
    global active_connections
    while True:
        active_connections = set(threading.enumerate())
        time.sleep(10)

def first_check():
    if ping():
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Connected\n")
    else:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Disconnected\n")

if __name__ == "__main__":
    first_check()
    threading.Thread(target=connection_tracking, daemon=True).start()
