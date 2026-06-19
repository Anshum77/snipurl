import requests
import time
import statistics
import uuid

BASE_URL = "http://localhost:8000"

RUNS = 20

create_times = []
redirect_times = []
stats_times = []
total_times = []

for i in range(RUNS):

    payload = {
        "url": "https://github.com/Anshum77/snipurl",
        "custom_alias": uuid.uuid4().hex[:8]
    }

    workflow_start = time.perf_counter()

    # ------------------
    # Create URL
    # ------------------

    start = time.perf_counter()

    response = requests.post(
        f"{BASE_URL}/shorten",
        json=payload
    )

    create_time = (time.perf_counter() - start) * 1000

    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        exit()

    data = response.json()

    short_url = data["short_url"]
    short_code = short_url.rstrip("/").split("/")[-1]

    # ------------------
    # Redirect
    # ------------------

    start = time.perf_counter()

    requests.get(
        f"{BASE_URL}/{short_code}",
        allow_redirects=False
    )

    redirect_time = (time.perf_counter() - start) * 1000

    # ------------------
    # Stats
    # ------------------

    start = time.perf_counter()

    requests.get(
        f"{BASE_URL}/{short_code}/stats"
    )

    stats_time = (time.perf_counter() - start) * 1000

    workflow_total = (time.perf_counter() - workflow_start) * 1000

    create_times.append(create_time)
    redirect_times.append(redirect_time)
    stats_times.append(stats_time)
    total_times.append(workflow_total)

# ----------------------
# Results
# ----------------------

print("\n===== RESULTS =====\n")

print("Create URL")
print("Average:", round(statistics.mean(create_times), 2), "ms")
print("Median :", round(statistics.median(create_times), 2), "ms")

print("\nRedirect")
print("Average:", round(statistics.mean(redirect_times), 2), "ms")
print("Median :", round(statistics.median(redirect_times), 2), "ms")

print("\nStats")
print("Average:", round(statistics.mean(stats_times), 2), "ms")
print("Median :", round(statistics.median(stats_times), 2), "ms")

print("\nTotal Workflow")
print("Average:", round(statistics.mean(total_times), 2), "ms")
print("Median :", round(statistics.median(total_times), 2), "ms")