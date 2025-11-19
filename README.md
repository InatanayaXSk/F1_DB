# Formula 1 Prediction System

A professional-grade F1 prediction system with advanced ML pipeline trained on 2023-2025 data. Features ensemble models (Gradient Boosting, Random Forest, XGBoost, LightGBM), comprehensive feature engineering with 20+ engineered features, and complete 2026 season predictions for Qualifying, Sprint, and Race sessions.

## Features

### Data & Storage
- **Multi-Year Data**: Complete 2023-2025 seasons from FastF1 API with automatic caching
- **SQLite Database**: 11-table schema with drivers, teams, races, results, predictions, and telemetry
- **Schema Migrations**: Automatic database upgrades without data loss
- **Telemetry Storage**: JSON files for detailed lap-by-lap telemetry data

### Machine Learning Pipeline
- **Advanced Models**: 4 ensemble models per session type (GB, RF, XGBoost, LightGBM)
- **10-Epoch Training**: 200 estimators per model for robust predictions
- **Feature Engineering**: 20+ features including historical performance, recent form, consistency metrics
- **Feature Weights**: Normalized importance scores showing which features drive predictions
- **Predictions**: Qualifying (24 races), Sprint (7 races), Race (24 races) positions for all 20 drivers
- **Confidence Scores**: Uncertainty quantification for each prediction
- **2026 Season**: Complete championship projections with driver name, team, and car number

### Interactive Dashboard
- **7-Page Streamlit UI**: Home, Drivers & Teams, 2026 Predictions, Database Explorer, Telemetry, Model Features, Importance
- **Driver Information**: Car numbers, full names, constructor teams visible throughout
- **Race-by-Race Predictions**: Top 10 predictions for each 2026 race with sprint indicators
- **Championship Projections**: Full drivers' and constructors' standings predictions
- **Offline Mode**: Works completely offline once data is cached

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Required packages include:
- `fastf1` - F1 data API
- `streamlit` - Interactive dashboard
- `plotly` - Visualizations
- `scikit-learn`, `xgboost`, `lightgbm`, `catboost` - ML models
- `shap` - Model explainability
- `pandas`, `numpy` - Data processing

2. **Cache F1 data (2023-2025 seasons):**
```bash
python src/data_fetcher.py
```
*Note: First run takes 45-90 minutes depending on internet speed*

3. **Initialize database:**
```bash
python src/database.py
```
*Creates SQLite database with all required tables and applies schema migrations*

## Usage

### Populate Database with 2023 Data

Extract data from FastF1 cache and populate database:
```bash
python src/populate_database.py
```
*Populates 20 drivers, 13 teams, 24 races, and all results from 2023 season*

### Training Models & Generating 2026 Predictions

Run the comprehensive ML pipeline notebook:
```bash
jupyter notebook notebooks/f1_2026_predictions.ipynb
```

**Pipeline Outputs:**
- Trained models saved to `models/` directory
- Feature importance analysis and visualizations
- Complete 2026 predictions (480 driver-race combinations)
- Championship projections (drivers & constructors)
- CSV exports for external analysis

### Streamlit Dashboard

Launch the interactive dashboard:
```bash
python -m streamlit run src/streamlit_app.py
```

The dashboard provides 7 comprehensive pages:

1. **Home** - System overview, features, and quick start guide
2. **Drivers & Teams** - Complete driver roster with car numbers, names, codes, and constructor/team affiliations (by season)
3. **2026 Predictions** - Race selector with top 10 predictions for each Grand Prix, championship standings projections
4. **Database Explorer** - Browse all database tables with enhanced driver information and custom SQL queries
5. **Telemetry Viewer** - Visualize cached telemetry files with interactive plots
6. **Model Predictions** - View predictions with driver names, team names, confidence scores, and visualizations
7. **Feature Importance** - Analyze which features influence predictions with weight analysis and importance charts

## Project Structure

```
Formula_1_db/
├── src/
│   ├── data_fetcher.py         # FastF1 data fetching and caching (2023-2025)
│   ├── database.py             # SQLite database with migrations
│   ├── populate_database.py    # Populate DB from FastF1 cache
│   ├── telemetry_handler.py    # JSON telemetry storage
│   └── streamlit_app.py        # 7-page Streamlit dashboard
├── notebooks/
│   └── f1_2026_predictions.ipynb  # Complete ML training & 2026 predictions
├── cache/                       # FastF1 cached data (2023-2025)
├── models/                      # Trained models, predictions, visualizations
├── requirements.txt             # Python dependencies
├── f1_data.db                  # SQLite database
└── README.md                   # This file
```

## ML Pipeline Architecture

### Training Data
- **Seasons**: 2023-2025 (3 complete seasons)
- **Samples**: 400+ race results with comprehensive telemetry
- **Features**: 20+ engineered features per prediction type

### Feature Engineering
**Qualifying Features (11):**
- Driver/team historical qualifying averages
- Recent form metrics (5-race rolling)
- Track-specific performance
- Total points, wins, podiums
- Consistency and DNF rate

**Race Features (15):**
- All qualifying features plus:
- Grid position and penalties
- Cumulative season points
- Team performance metrics
- Position gain/loss patterns

**Sprint Features (9):**
- Subset of race features optimized for short-format racing

### Model Ensemble
**4 Models per Session Type:**
- **Gradient Boosting**: n_estimators=200, learning_rate=0.05, max_depth=6
- **Random Forest**: n_estimators=200, max_depth=12
- **XGBoost**: n_estimators=200, learning_rate=0.05, max_depth=6
- **LightGBM**: n_estimators=200, learning_rate=0.05, max_depth=6

**Training**: 10 epochs × 20 base estimators = 200 estimators per model

### Prediction Output
1. **Qualifying positions** - Starting grid for all 24 races
2. **Sprint race results** - 7 sprint weekends (China, Miami, Austria, Belgium, COTA, Brazil, Qatar)
3. **Main race results** - Final positions for all 24 races
4. **Championship projections** - Full drivers' and constructors' standings
5. **Confidence scores** - Ensemble variance-based uncertainty
6. **Feature weights** - Normalized importance showing key predictors

### Features Used
- Driver/team historical performance
- Recent form (last 3-5 races)
- Qualifying position
- Grid position
- Track-specific statistics
- Weather conditions
- Tyre compound strategies
- Pit stop patterns

## Data Sources

- FastF1 API for official F1 timing data
- Historical race results (2023-2025 seasons)
- Driver and team information
- Circuit characteristics
- Weather conditions

## Database Schema

The SQLite database includes:
- **drivers** - Driver information with car numbers and teams (by year)
- **teams** - Constructor/team information
- **races** - Race calendar and event details
- **qualifying_results** - Q1, Q2, Q3 session results
- **sprint_results** - Sprint race results
- **race_results** - Main race results with points
- **predictions** - Model predictions with confidence, SHAP values, and metadata
- **aggregated_laps** - Lap-by-lap data for analysis
- **tyre_stats** - Tyre compound performance data
- **sessions** - Session-level metadata

## Offline Mode

Once data is cached:
1. **FastF1 cache** - Stored locally in `cache/` directory (2023-2025)
2. **SQLite database** - Persists all structured data in `f1_data.db`
3. **JSON telemetry** - Detailed telemetry snapshots
4. **Trained models** - Saved in `models/` directory with metadata
5. **No internet required** - System fully functional offline after initial setup

## Performance Notes

- **Data fetching**: 45-90 minutes for first run (3 seasons)
- **Subsequent runs**: 1-2 minutes (uses cache)
- **Model training**: 5-15 minutes depending on features
- **Predictions**: Near-instant once models are trained
- **Database queries**: Optimized with indexes for fast retrieval

## Troubleshooting

**Missing columns error**: Run `python src/database.py` to apply schema migrations

**Import errors**: Ensure all dependencies installed via `pip install -r requirements.txt`

**Streamlit not found**: Use `python -m streamlit run src/streamlit_app.py`

**No data in dashboard**: Run data fetcher and database initialization first

## License

MIT License