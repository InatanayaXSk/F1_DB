# F1 Prediction System - Project Summary

## Overview

The F1 Prediction System is a comprehensive, professional-grade machine learning application designed to predict Formula 1 race outcomes, qualifying positions, and sprint race results. The system leverages historical F1 data from 2023-2025 seasons, advanced feature engineering, and ensemble machine learning models to generate predictions for the 2026 season.

## Project Purpose

This system provides:
- **Data Collection & Storage**: Automated fetching and caching of F1 data from the official FastF1 API
- **Database Management**: SQLite-based storage for structured race data, driver information, and predictions
- **Machine Learning Pipeline**: Advanced ML models for predicting race outcomes with high accuracy
- **Interactive Dashboard**: Streamlit-based web interface for data exploration and visualization
- **Offline Capability**: Complete functionality without internet after initial data fetch
- **Explainability**: Feature importance analysis and model confidence metrics

## Core Features

### 1. Data Management
- **FastF1 API Integration**: Official F1 timing data access
- **Multi-Year Data**: Complete 2023-2025 seasons with automatic caching
- **Offline-First Design**: All data cached locally for offline operation
- **Dual Storage System**:
  - SQLite database for structured data (11 tables)
  - JSON files for detailed telemetry data

### 2. Database Schema (11 Tables)

#### Core Tables
1. **drivers** - Driver information with car numbers and team associations
   - driver_id (PK), driver_number, abbreviation, full_name, team_name, year
   - Unique constraint: (driver_number, year)

2. **teams** - Constructor/team information
   - team_id (PK), team_name, year
   - Unique constraint: (team_name, year)

3. **races** - Race calendar and event details
   - race_id (PK), year, round_number, event_name, country, location, event_date
   - Unique constraint: (year, round_number)

#### Results Tables
4. **qualifying_results** - Q1, Q2, Q3 session results
   - result_id (PK), race_id (FK), driver_number, position, q1_time, q2_time, q3_time

5. **sprint_results** - Sprint race results
   - result_id (PK), race_id (FK), driver_number, position, points, status

6. **race_results** - Main race results with points
   - result_id (PK), race_id (FK), driver_number, position, points, grid_position, status, fastest_lap_time

#### Predictions & Analytics Tables
7. **predictions** - Model predictions with confidence and SHAP values
   - prediction_id (PK), race_id (FK), session_type, driver_number, predicted_position, predicted_time, confidence, top10_probability, model_type, prediction_date, features_json, shap_values_json

8. **aggregated_laps** - Lap-by-lap data for analysis
   - lap_id (PK), race_id (FK), session_type, driver_number, lap_number, lap_time, sector1_time, sector2_time, sector3_time, compound, tyre_life, track_status, is_personal_best

9. **tyre_stats** - Tyre compound performance data
   - tyre_stat_id (PK), race_id (FK), session_type, driver_number, compound, total_laps, avg_lap_time, degradation_slope, best_lap_time, stint_number

10. **sessions** - Session-level metadata
    - session_id (PK), race_id (FK), session_type, session_date, weather_conditions, track_temp, air_temp
    - Unique constraint: (race_id, session_type)

### 3. Machine Learning Pipeline

#### Models
The system employs an ensemble approach with 4 models per session type:
- **Gradient Boosting**: Complex pattern recognition (200 estimators, learning_rate=0.05, max_depth=6)
- **Random Forest**: Robust predictions with feature importance (200 estimators, max_depth=12)
- **XGBoost**: Gradient boosting optimization (200 estimators, learning_rate=0.05, max_depth=6)
- **LightGBM**: Lightweight gradient boosting (200 estimators, learning_rate=0.05, max_depth=6)

#### Training
- **10-Epoch Training**: 200 estimators per model for robust predictions
- **Cross-Validation**: Model evaluation with train-test splits
- **Feature Scaling**: StandardScaler for normalization

#### Feature Engineering
The system uses 20+ engineered features:

**Qualifying Features (11):**
- Driver historical qualifying averages
- Recent form metrics (5-race rolling window)
- Track-specific performance
- Total points, wins, podiums
- Consistency metrics and DNF rate

**Race Features (15):**
- All qualifying features plus:
- Grid position and penalties
- Cumulative season points
- Team performance metrics
- Position gain/loss patterns
- Tyre strategy indicators

**Sprint Features (9):**
- Optimized subset for short-format racing
- Focus on recent form and qualifying position

### 4. Prediction Capabilities

#### 2026 Season Predictions
- **24 Qualifying Sessions**: Starting grid predictions for all races
- **7 Sprint Races**: Results for China, Miami, Austria, Belgium, COTA, Brazil, Qatar
- **24 Main Races**: Final position predictions with points allocation
- **Championship Standings**: Drivers' and constructors' championship projections
- **Confidence Scores**: Ensemble variance-based uncertainty quantification

#### Prediction Outputs
- Top 10 predictions for each session
- Driver name, team, car number visible throughout
- Confidence intervals and probability metrics
- Feature importance for each prediction
- SHAP values for explainability

### 5. Interactive Dashboard (Streamlit)

#### 7-Page Interface
1. **Home** - System overview, features, quick start guide
2. **Drivers & Teams** - Complete driver roster with car numbers, names, codes, constructor affiliations
3. **2026 Predictions** - Race selector, top 10 predictions per Grand Prix, championship standings
4. **Database Explorer** - Browse all tables, custom SQL queries, CSV export
5. **Telemetry Viewer** - Visualize cached telemetry with interactive plots
6. **Model Predictions** - View predictions with confidence scores and visualizations
7. **Feature Importance** - Analyze feature weights and importance charts

## Technical Architecture

### Data Flow
```
FastF1 API → Data Fetcher → Cache Directory
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
SQLite DB   JSON Files   ML Models
    ↓           ↓           ↓
    └───────────┼───────────┘
                ↓
        Streamlit Dashboard
```

### Module Structure

#### `src/data_fetcher.py` (169 lines)
- FastF1 API integration
- Data caching mechanism
- Session data retrieval (FP1, FP2, FP3, Qualifying, Sprint, Race)
- Historical data batch processing

**Key Methods:**
- `fetch_season_schedule(year)` - Get race calendar
- `fetch_race_results(year, event)` - Race results
- `fetch_qualifying_results(year, event)` - Qualifying results
- `fetch_sprint_results(year, event)` - Sprint results
- `fetch_driver_lap_data(year, event, session_type)` - Lap data
- `fetch_telemetry_data(year, event, driver_number, session_type)` - Telemetry

#### `src/database.py` (529 lines)
- SQLite database management
- 11-table schema with relationships
- CRUD operations for all entities
- Schema migration support
- Query utilities and data export

**Key Methods:**
- `initialize_database()` - Create all tables
- `upgrade_database()` - Schema migrations
- `insert_driver()`, `insert_team()`, `insert_race()` - Data insertion
- `insert_qualifying_result()`, `insert_race_result()` - Results storage
- `insert_prediction()` - Store ML predictions
- `get_all_races()`, `get_race_results()`, `get_predictions()` - Data retrieval
- `execute_query()` - Custom SQL execution

#### `src/telemetry_handler.py` (200 lines)
- JSON-based telemetry storage
- Organized directory structure (year/event/session)
- Metadata tracking
- Efficient load/save operations

**Key Methods:**
- `save_telemetry(year, event, driver, session_type, telemetry_df)` - Save telemetry
- `load_telemetry(year, event, driver, session_type)` - Load telemetry
- `save_lap_data(year, event, session_type, laps_df)` - Save lap data
- `list_available_telemetry()` - List cached files

#### `src/ml_models.py` (324 lines)
- Machine learning model implementations
- Ensemble prediction methods
- Feature importance analysis
- Model persistence (save/load)

**Key Methods:**
- `prepare_features(data)` - Feature extraction
- `train_gradient_boosting(X_train, y_train)` - GB model training
- `train_random_forest(X_train, y_train)` - RF model training
- `train_ensemble(X, y)` - Train all models
- `predict(X, model_type)` - Generate predictions
- `get_feature_importance(model_type)` - Feature analysis
- `save_models(name)`, `load_models(name)` - Model persistence

#### `src/feature_engineering.py` (200+ lines)
- Advanced feature extraction
- Tyre degradation analysis
- Speed percentile calculations
- Throttle/brake variance metrics
- Driver and team history tracking

**Key Methods:**
- `calculate_tyre_degradation(lap_times, tyre_life)` - Degradation slope
- `calculate_speed_percentiles(speed_data)` - Speed statistics
- `calculate_throttle_brake_variance(throttle_data, brake_data)` - Driver smoothness

#### `src/streamlit_app.py` (390 lines)
- Interactive web dashboard
- 7-page navigation
- Data visualization with Plotly
- Database exploration interface
- Telemetry viewer

#### `src/populate_database.py` (198 lines)
- Database population from FastF1 cache
- Batch processing for multiple seasons
- Driver, team, race, and results insertion
- Progress tracking and error handling

#### `src/advanced_ml_models.py`
- Extended ML capabilities
- Additional model types (XGBoost, LightGBM, CatBoost)
- SHAP value computation
- Advanced ensemble techniques

### Notebooks

#### `notebooks/f1_2026_predictions.ipynb` (525 lines)
Complete ML training and prediction pipeline:
1. Data collection from FastF1
2. Feature engineering
3. Model training (10 epochs)
4. Cross-validation and evaluation
5. Feature importance visualization
6. 2026 season predictions
7. Championship projections
8. CSV exports and model storage

## Technology Stack

### Languages & Frameworks
- **Python 3.x** - Core programming language
- **Streamlit** - Interactive web dashboard
- **Jupyter** - ML pipeline notebooks

### Data & Storage
- **FastF1** - Official F1 data API
- **SQLite** - Structured database (11 tables)
- **JSON** - Telemetry data storage
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations

### Machine Learning
- **Scikit-learn** - Core ML framework
  - GradientBoostingRegressor
  - RandomForestRegressor
  - StandardScaler, cross_val_score
- **XGBoost** - Gradient boosting optimization
- **LightGBM** - Lightweight gradient boosting
- **CatBoost** - Categorical boosting
- **SHAP** - Model explainability
- **SciPy** - Statistical analysis

### Visualization
- **Plotly** - Interactive charts and graphs
- **Matplotlib** - Static plots
- **Seaborn** - Statistical graphics

### Utilities
- **papermill** - Notebook parameterization
- **nbconvert** - Notebook conversion
- **joblib** - Model serialization

## Key Relationships

### Entity Relationships
1. **Drivers ↔ Teams**: Many-to-many through year association
2. **Races ↔ Results**: One-to-many (one race has many results)
3. **Races ↔ Sessions**: One-to-many (one race has multiple sessions)
4. **Races ↔ Predictions**: One-to-many (one race has predictions for all drivers)
5. **Predictions → Drivers**: Many-to-one (predictions reference drivers by number)
6. **Aggregated Laps → Races**: Many-to-one (laps belong to specific races)
7. **Tyre Stats → Races**: Many-to-one (tyre stats per race session)

## Usage Workflow

### Initial Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Cache F1 data (2023-2025)
python src/data_fetcher.py  # 45-90 minutes first run

# 3. Initialize database
python src/database.py

# 4. Populate database
python src/populate_database.py
```

### Training & Predictions
```bash
# Train models and generate 2026 predictions
jupyter notebook notebooks/f1_2026_predictions.ipynb
```

### Dashboard Access
```bash
# Launch interactive dashboard
python -m streamlit run src/streamlit_app.py
# Access at http://localhost:8501
```

## Performance Characteristics

- **Data Fetching**: 45-90 minutes (first run), 1-2 minutes (cached)
- **Model Training**: 5-15 minutes per session type
- **Predictions**: Near-instant once models trained
- **Database Queries**: Optimized with indexes
- **Offline Mode**: Fully functional after initial setup

## Security & Best Practices

- **Read-Only SQL**: Custom queries restricted to SELECT only
- **Input Validation**: Sanitized inputs for all user queries
- **No Hardcoded Credentials**: Environment-based configuration
- **Data Integrity**: Foreign key constraints and unique indexes
- **Error Handling**: Comprehensive try-catch blocks
- **Schema Migrations**: Non-destructive database upgrades

## Future Enhancement Possibilities

- Real-time data updates during race weekends
- Advanced feature engineering (weather, tire compounds)
- Deep learning models (LSTM for time series)
- Mobile-responsive dashboard
- REST API endpoints for external access
- Automated model retraining pipeline
- Performance optimization for large datasets
- Multi-season championship analysis
- Driver comparison tools
- Team strategy recommendations

## File Structure Summary

```
F1_DB/
├── src/                          # Source code modules
│   ├── __init__.py
│   ├── data_fetcher.py          # FastF1 API integration
│   ├── database.py              # SQLite management
│   ├── populate_database.py     # Data population scripts
│   ├── telemetry_handler.py     # JSON telemetry storage
│   ├── ml_models.py             # ML models (GB, RF)
│   ├── advanced_ml_models.py    # Extended ML (XGB, LGBM, CB)
│   ├── feature_engineering.py   # Feature extraction
│   └── streamlit_app.py         # Interactive dashboard
├── notebooks/
│   └── f1_2026_predictions.ipynb # ML training pipeline
├── docs/                         # Documentation
│   ├── summary.md               # This file
│   └── dgm.md                   # ER diagram (to be created)
├── cache/                        # FastF1 cached data (2023-2025)
├── models/                       # Trained ML models
├── telemetry_data/              # JSON telemetry files
├── f1_data.db                   # SQLite database
├── ARCHITECTURE.md              # System architecture
├── IMPLEMENTATION_SUMMARY.md    # Implementation details
├── README.md                    # Project overview
├── USAGE.md                     # Usage instructions
├── requirements.txt             # Python dependencies
├── demo.py                      # Demonstration script
└── setup.sh                     # Setup automation script
```

## Total Project Size
- **~3,000+ lines of code**
- **11 database tables**
- **8 Python modules**
- **4 ML model types**
- **20+ engineered features**
- **Comprehensive documentation**

## Conclusion

The F1 Prediction System is a production-ready, professional-grade application that combines official F1 data, robust database design, advanced machine learning, and an intuitive user interface. The system is fully offline-capable, highly explainable, and designed for both technical users (via Jupyter notebooks) and non-technical users (via Streamlit dashboard). All predictions are stored in a well-structured SQLite database with proper relationships, constraints, and indexes for optimal performance.
