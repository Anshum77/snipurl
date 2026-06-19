# End-to-End Workflow Benchmark

## Environment

- FastAPI
- PostgreSQL 16
- Redis 7
- Docker Compose
- Windows 11
- Localhost testing

## Methodology

For each run:

1. Create a new short URL
2. Perform a redirect request
3. Fetch analytics stats

20 workflow runs were executed.

## Results

| Operation | Average | Median |
|------------|------------|------------|
| Create URL | 13.60 ms | 12.06 ms |
| Redirect | 7.95 ms | 7.78 ms |
| Stats | 12.55 ms | 11.64 ms |
| Total Workflow | 34.13 ms | 31.53 ms |

## Conclusion

The complete URL lifecycle (creation, redirect, analytics retrieval) completed in approximately 34 ms on average in a Dockerized FastAPI + PostgreSQL + Redis environment.