# Changelog

All notable changes to the F1 Prediction System.

## [2.0.0] - 2025-11-19

### Major Changes - PostgreSQL & Redis Migration

This is a major architectural update that replaces SQLite and local file caching with PostgreSQL and Redis.

### Added

- **PostgreSQL Support**: Professional-grade relational database
  - Full schema migration from SQLite
  - Environment variable configuration
  - Better scalability and performance
  
- **Redis Caching**: In-memory caching for F1 data
  - Custom RedisCache class with pickle serialization
  - 24-hour TTL for cached data
  - Significantly faster than local file I/O
  
- **Docker Support**: Easy setup with Docker Compose
  - PostgreSQL 15 container
  - Redis 7 container
  - Volume persistence
  - Health checks
  
- **Setup Automation**: New setup.py script
  - Automated Docker setup
  - Dependency installation
  - Database initialization
  - Step-by-step guidance
  
- **Configuration Management**:
  - `.env.example` for environment variables
  - Flexible PostgreSQL/Redis configuration
  - Default values for quick start
  
- **Documentation**:
  - `MIGRATION.md` - Complete migration guide
  - `QUICK_START.md` - Get started in minutes
  - `CHANGELOG.md` - This file
  - Updated `README.md` with new setup instructions
  - Updated `ARCHITECTURE.md` with new diagrams

### Changed

- **Database Layer** (`src/database.py`):
  - Replaced `sqlite3` with `psycopg2`
  - Changed `AUTOINCREMENT` to `SERIAL` (PostgreSQL syntax)
  - Updated table introspection queries
  - Added environment variable support
  
- **Data Fetcher** (`src/data_fetcher.py`):
  - Removed local cache directory dependency
  - Added Redis caching with automatic fallback
  - Implemented pickle-based serialization
  - Added TTL support for cached data
  
- **Database Population** (`src/populate_database.py`):
  - Updated to use new Redis-based fetcher
  - Removed local cache directory references
  
- **Streamlit App** (`src/streamlit_app.py`):
  - Updated feature descriptions
  - Changed references from SQLite to PostgreSQL
  - Updated cache descriptions

### Removed

- **Local File Cache**: No more `cache/` directory
  - Eliminated slow file I/O operations
  - Freed up disk space
  - Improved performance significantly
  
- **SQLite Database**: No more `f1_data.db` file
  - Migrated to PostgreSQL for production readiness
  - Better scalability and reliability

### Performance Improvements

- **Redis Caching**: Instant cache access vs 100-1000ms+ for file I/O
- **PostgreSQL**: Better query performance with proper indexes
- **No Disk I/O**: All F1 data cached in memory (Redis)
- **Faster Startup**: Quick access to cached data

### Breaking Changes

⚠️ **This is a breaking change** - The system now requires:
- PostgreSQL database (instead of SQLite)
- Redis server (instead of local cache folder)
- Docker (recommended) or manual PostgreSQL/Redis installation

**Migration Path**: See [MIGRATION.md](MIGRATION.md) for step-by-step upgrade instructions.

### Security

- CodeQL scan: 0 vulnerabilities
- GitHub Advisory Database: No vulnerable dependencies
- All new dependencies vetted for security

### Dependencies Added

- `psycopg2-binary>=2.9.0` - PostgreSQL adapter
- `redis>=5.0.0` - Redis client

### Dependencies Removed

- None (only SQLite was built-in)

---

## [1.0.0] - Previous

Initial release with:
- SQLite database
- Local file caching
- FastF1 integration
- ML prediction models
- Streamlit dashboard
