# Cached Redirect Latency Distribution Benchmark

## Environment

- FastAPI
- PostgreSQL 16
- Redis 7
- Docker Compose
- Windows 11
- Localhost testing

## Methodology

1. Created a benchmark short URL.
2. Warmed the Redis cache by performing an initial redirect request.
3. Executed 1000 cached redirect requests.
4. Measured latency distribution across all requests.

Endpoint tested:

GET /benchmark

## Results

| Metric | Latency |
|----------|----------|
| Average | 6.63 ms |
| Median | 6.42 ms |
| P50 | 6.42 ms |
| P95 | 8.26 ms |
| P99 | 9.95 ms |
| Min | 5.52 ms |
| Max | 12.38 ms |

## Conclusion

- Maintained sub-10 ms P99 latency across 1000 cached redirect requests.
- 95% of requests completed within 8.26 ms.
- 99% of requests completed within 9.95 ms.
- Maximum observed latency was 12.38 ms.

These results demonstrate consistent low-latency performance for Redis-cached URL redirects.