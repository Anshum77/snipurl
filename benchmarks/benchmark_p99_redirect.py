import requests
import time
import statistics

URL = "http://localhost:8000/benchmark"

NUM_REQUESTS = 1000

times = []

print(f"Running {NUM_REQUESTS} redirect requests...")

for _ in range(NUM_REQUESTS):
    start = time.perf_counter()

    requests.get(
        URL,
        allow_redirects=False,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    times.append(elapsed_ms)

times.sort()

p50 = times[int(0.50 * NUM_REQUESTS)]
p95 = times[int(0.95 * NUM_REQUESTS)]
p99 = times[int(0.99 * NUM_REQUESTS)]

print("\n===== RESULTS =====\n")

print("Requests:", NUM_REQUESTS)

print("Average:", round(statistics.mean(times), 2), "ms")
print("Median :", round(statistics.median(times), 2), "ms")

print("P50    :", round(p50, 2), "ms")
print("P95    :", round(p95, 2), "ms")
print("P99    :", round(p99, 2), "ms")

print("Min    :", round(min(times), 2), "ms")
print("Max    :", round(max(times), 2), "ms")