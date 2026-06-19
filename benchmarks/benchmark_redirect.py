import requests
import time
import statistics

URL = "http://localhost:8000/benchmark"

times = []

for _ in range(100):
    start = time.perf_counter()

    requests.get(URL, allow_redirects=False)

    end = time.perf_counter()

    times.append((end - start) * 1000)

print("Average:", round(statistics.mean(times), 2), "ms")
print("Median :", round(statistics.median(times), 2), "ms")
print("Min    :", round(min(times), 2), "ms")
print("Max    :", round(max(times), 2), "ms")