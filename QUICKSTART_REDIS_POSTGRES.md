# Quick Start: Redis & PostgreSQL

This guide helps you quickly set up Redis caching and PostgreSQL for the F1 Prediction System.

## Option 1: SQLite Only (Default - No Setup Required)

The system works out of the box with SQLite:

```bash
pip install -r requirements.txt
python src/database.py
python src/populate_database.py
streamlit run src/streamlit_app.py
```

## Option 2: SQLite + Redis Caching (Recommended for Development)

### Step 1: Install Redis

**Using Docker (Easiest):**
```bash
docker run -d -p 6379:6379 --name f1-redis redis:latest
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install redis-server -y
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### Step 2: Configure

Create `.env` file:
```bash
cat > .env << 'EOF'
DB_TYPE=sqlite
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
```

### Step 3: Verify

```bash
# Test Redis connection
redis-cli ping  # Should return: PONG

# Run tests
python test_redis_postgres.py
```

### Step 4: Use Enhanced Database

```python
from src.database_enhanced import F1DatabaseEnhanced

db = F1DatabaseEnhanced()
races = db.get_all_races()  # First call - queries DB
races = db.get_all_races()  # Second call - from cache (10-100x faster!)
```

## Option 3: PostgreSQL + Redis (Production)

### Step 1: Install PostgreSQL & Redis

**Using Docker Compose (Recommended):**

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: f1_database
      POSTGRES_USER: f1_user
      POSTGRES_PASSWORD: f1_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Start services:
```bash
docker-compose up -d
```

**Manual Installation:**

Ubuntu/Debian:
```bash
# PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql

# Create database
sudo -u postgres psql -c "CREATE DATABASE f1_database;"
sudo -u postgres psql -c "CREATE USER f1_user WITH PASSWORD 'f1_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE f1_database TO f1_user;"

# Redis
sudo apt install redis-server -y
sudo systemctl start redis-server
```

macOS:
```bash
# PostgreSQL
brew install postgresql
brew services start postgresql
createdb f1_database

# Redis
brew install redis
brew services start redis
```

### Step 2: Configure

Create `.env` file:
```bash
cat > .env << 'EOF'
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=f1_database
POSTGRES_USER=f1_user
POSTGRES_PASSWORD=f1_password

REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
```

### Step 3: Migrate Data (if you have existing SQLite data)

```bash
python src/migrate_to_postgres.py
```

This will:
- Transfer all data from SQLite to PostgreSQL
- Verify data integrity
- Show migration report

### Step 4: Verify Setup

```bash
# Test PostgreSQL connection
psql -h localhost -U f1_user -d f1_database -c "SELECT version();"

# Test Redis connection
redis-cli ping

# Run comprehensive tests
python test_redis_postgres.py
```

Expected output:
```
============================================================
Test Summary
============================================================
✓ PASS: Configuration
✓ PASS: Redis Cache
✓ PASS: Enhanced Database
✓ PASS: Backward Compatibility
✓ PASS: Cache Performance

Total: 5/5 tests passed

🎉 All tests passed!
```

## Configuration Quick Reference

### SQLite (Default)
```env
DB_TYPE=sqlite
REDIS_ENABLED=false
```

### SQLite + Redis
```env
DB_TYPE=sqlite
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### PostgreSQL + Redis
```env
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=f1_database
POSTGRES_USER=f1_user
POSTGRES_PASSWORD=your_password

REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Usage Examples

### Automatic Database Selection

```python
from src.database import get_database_instance

# Automatically uses the right database based on .env
db = get_database_instance()
```

### Explicit Enhanced Database

```python
from src.database_enhanced import F1DatabaseEnhanced

db = F1DatabaseEnhanced()

# All queries are automatically cached
races = db.get_all_races()
predictions = db.get_predictions(race_id=1)

# Check cache performance
stats = db.get_cache_stats()
print(f"Cache hit rate: {stats.get('keyspace_hits', 0)}")
```

### Cache Management

```python
from src.redis_cache import get_cache_instance

cache = get_cache_instance()

# Flush all cache
cache.flush_all()

# Invalidate specific patterns
cache.delete_pattern('race:*')
cache.invalidate_race_cache(race_id=1)

# View statistics
stats = cache.get_stats()
print(stats)
```

## Performance Comparison

| Configuration | Query Time | Notes |
|--------------|------------|-------|
| SQLite | 50-200ms | Default, good for development |
| SQLite + Redis | 1-5ms | 10-100x faster for repeated queries |
| PostgreSQL | 30-150ms | Better concurrency, production-ready |
| PostgreSQL + Redis | 1-5ms | Best performance, recommended for production |

## Troubleshooting

### Redis not connecting
```bash
# Check if Redis is running
redis-cli ping

# If not, start it
docker start f1-redis  # Docker
# OR
sudo systemctl start redis-server  # Linux
# OR
brew services start redis  # macOS
```

### PostgreSQL connection refused
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check credentials
psql -h localhost -U f1_user -d f1_database

# Verify database exists
psql -U postgres -c "\l"
```

### Migration fails
```bash
# Check source database exists
ls -lh f1_data.db

# Verify target database is accessible
psql -h localhost -U f1_user -d f1_database -c "SELECT 1;"

# Run migration with verbose output
python src/migrate_to_postgres.py
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Docker Compose Full Stack

For a complete production setup:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: f1_database
      POSTGRES_USER: f1_user
      POSTGRES_PASSWORD: f1_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U f1_user"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  f1-app:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DB_TYPE: postgresql
      POSTGRES_HOST: postgres
      POSTGRES_DB: f1_database
      POSTGRES_USER: f1_user
      POSTGRES_PASSWORD: f1_password
      REDIS_ENABLED: "true"
      REDIS_HOST: redis
    ports:
      - "8501:8501"
    command: streamlit run src/streamlit_app.py

volumes:
  postgres_data:
```

Start everything:
```bash
docker-compose up -d
```

## Next Steps

1. ✅ Setup complete - verify with `python test_redis_postgres.py`
2. 📊 Populate data - `python src/populate_database.py`
3. 🎯 Train models - Open `notebooks/f1_2026_predictions.ipynb`
4. 🚀 Launch dashboard - `streamlit run src/streamlit_app.py`

## Support

- **Full Guide**: See [REDIS_POSTGRES_GUIDE.md](REDIS_POSTGRES_GUIDE.md)
- **Configuration**: See [.env.example](.env.example)
- **Issues**: Check troubleshooting sections above

Enjoy your high-performance F1 prediction system! 🏎️💨
