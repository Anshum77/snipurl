# Redirect Latency Benchmark

## Environment

- FastAPI
- PostgreSQL 16
- Redis 7
- Docker Compose
- Windows 11
- Localhost testing

## Test Methodology

1. Created a benchmark short URL.
2. Deleted the Redis cache entry.
3. Measured the first redirect request (cold cache).
4. Measured 100 subsequent redirect requests after cache population (warm cache).

## Results

### Cold Cache

| Metric | Value |
|----------|----------|
| Redirect Latency | 1461.88 ms |

### Warm Cache (100 Requests)

| Metric | Value |
|----------|----------|
| Average | 13.74 ms |
| Median | 13.19 ms |
| Min | 9.51 ms |
| Max | 41.72 ms |

## Improvement

Latency reduction:

((1461.88 - 13.74) / 1461.88) * 100

= 99.06%

## Conclusion

Redis cache-aside lookups reduced repeat redirect latency by approximately 99% compared to a cold-cache request in the local Docker environment.

## Benchmarks

### Redirect Latency (Cold vs Warm Cache)

| Scenario | Latency |
|-----------|-----------|
| Cold Cache | 1461.88 ms |
| Warm Cache (avg) | 13.74 ms |

Result:

- ~99% lower latency for repeated redirects using Redis cache-aside lookups.

Benchmark scripts and methodology are available in `/benchmarks`.