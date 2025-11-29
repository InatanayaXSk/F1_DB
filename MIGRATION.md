# Migration Guide: SQLite to PostgreSQL & Local Cache to Redis

This guide helps you migrate from the old architecture (SQLite + local file cache) to the new architecture (PostgreSQL + Redis).

## Why Migrate?

### Performance Benefits
- **Redis**: In-memory caching is significantly faster than local file I/O
- **PostgreSQL**: More robust and scalable than SQLite
- **No Local Cache Files**: Eliminates disk space issues and slow file operations

### Architecture Benefits
- **Production-ready**: PostgreSQL and Redis are industry-standard production databases
- **Scalability**: Can handle more data and concurrent users
- **Reliability**: Better transaction support and data integrity

## Migration Steps

### 1. Start PostgreSQL and Redis

Using Docker (recommended):
```bash
docker-compose up -d
```

This starts:
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

Or install manually:
- PostgreSQL: https://www.postgresql.org/download/
- Redis: https://redis.io/download

### 2. Configure Environment (Optional)

If using non-default settings:
```bash
cp .env.example .env
# Edit .env with your settings
```

Default configuration:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=f1_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Install New Dependencies

```bash
pip install -r requirements.txt
```

This adds:
- `psycopg2-binary` - PostgreSQL adapter
- `redis` - Redis client

### 4. Initialize PostgreSQL Database

```bash
python src/database.py
```

This creates all required tables in PostgreSQL.

### 5. Cache F1 Data in Redis

```bash
python src/data_fetcher.py
```

This caches 2023-2025 F1 data in Redis (replaces local `cache/` folder).

### 6. Populate PostgreSQL Database

```bash
python src/populate_database.py
```

This populates PostgreSQL with F1 data from Redis cache.

### 7. Clean Up Old Data (Optional)

You can now safely remove:
- `cache/` folder (if it exists)
- `f1_data.db` file (SQLite database)

```bash
rm -rf cache/
rm -f f1_data.db
```

## Verification

1. **Check PostgreSQL**:
```bash
docker exec -it f1_postgres psql -U postgres -d f1_data -c "SELECT COUNT(*) FROM drivers;"
```

2. **Check Redis**:
```bash
docker exec -it f1_redis redis-cli DBSIZE
```

3. **Run Streamlit**:
```bash
python -m streamlit run src/streamlit_app.py
```

## Rollback

If you need to rollback to the old architecture:

1. Check out the previous commit
2. Stop Docker containers: `docker-compose down`
3. Reinstall old dependencies: `pip install -r requirements.txt`

## Troubleshooting

### PostgreSQL Connection Issues
```
psycopg2.OperationalError: could not connect to server
```
**Solution**: Ensure PostgreSQL is running and environment variables are correct.

### Redis Connection Issues
```
redis.exceptions.ConnectionError: Error connecting to Redis
```
**Solution**: Ensure Redis is running on the configured host/port.

### Data Not Found
```
No data in dashboard
```
**Solution**: Run `python src/data_fetcher.py` to populate Redis cache, then `python src/populate_database.py` to populate PostgreSQL.

### Performance Issues
- Redis should respond in milliseconds
- PostgreSQL queries should be fast with proper indexes
- If slow, check Docker resource allocation

## Support

For issues, please check:
1. Docker containers are running: `docker-compose ps`
2. Environment variables are set correctly
3. Dependencies are installed: `pip list | grep -E "psycopg2|redis"`
