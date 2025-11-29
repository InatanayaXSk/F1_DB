# Quick Start Guide

Get up and running with the F1 Prediction System in minutes!

## Prerequisites

- Python 3.8+
- Docker Desktop (for PostgreSQL and Redis)

## Installation (3 Steps)

### Step 1: Clone and Setup

```bash
git clone https://github.com/InatanayaXSk/F1_DB.git
cd F1_DB
python setup.py
```

The setup script will:
- Check Docker installation
- Start PostgreSQL and Redis
- Install Python dependencies
- Initialize the database

### Step 2: Cache F1 Data

```bash
python src/data_fetcher.py
```

This caches 2023-2025 F1 seasons in Redis (takes 45-90 minutes first time).

### Step 3: Populate Database

```bash
python src/populate_database.py
```

This populates PostgreSQL with F1 data from Redis cache.

## Usage

### Launch Dashboard

```bash
python -m streamlit run src/streamlit_app.py
```

Then open http://localhost:8501 in your browser.

### Train ML Models

```bash
jupyter notebook notebooks/f1_2026_predictions.ipynb
```

## Configuration

Default configuration (works out of the box):
- PostgreSQL: localhost:5432
- Redis: localhost:6379

To customize, create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Stopping Services

```bash
docker-compose down
```

## Troubleshooting

**Docker not running?**
```bash
# Start Docker Desktop, then:
docker-compose up -d
```

**Connection errors?**
```bash
# Check services are running:
docker-compose ps

# Restart services:
docker-compose restart
```

**Need to reset everything?**
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Start fresh
python setup.py         # Re-initialize
```

## Next Steps

- 📖 See [README.md](README.md) for detailed documentation
- 🔄 See [MIGRATION.md](MIGRATION.md) if upgrading from old version
- 🏗️ See [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review [README.md](README.md) and [MIGRATION.md](MIGRATION.md)
3. Open an issue on GitHub
