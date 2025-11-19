# F1 Prediction System - Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/InatanayaXSk/Formula_1_db.git
cd Formula_1_db

# Run setup script
bash setup.sh
```

### 2. Running the Demo

```bash
python demo.py
```

This will:
- Initialize the database
- Create sample data
- Train basic ML models
- Store predictions
- Display feature importance

### 3. Streamlit Dashboard

```bash
streamlit run src/streamlit_app.py
```

Access the dashboard at `http://localhost:8501`

### 4. Training ML Models

```bash
jupyter notebook notebooks/f1_ml_pipeline.ipynb
```

## Components Overview

### Data Fetcher (`src/data_fetcher.py`)

Fetches F1 data using FastF1 API and caches it locally.

```python
from src.data_fetcher import F1DataFetcher

fetcher = F1DataFetcher()

# Fetch season schedule
schedule = fetcher.fetch_season_schedule(2024)

# Fetch race results
results = fetcher.fetch_race_results(2024, "Bahrain Grand Prix")

# Fetch qualifying results
quali = fetcher.fetch_qualifying_results(2024, "Bahrain Grand Prix")

# Cache historical data (2023-2024)
fetcher.cache_historical_data(start_year=2023, end_year=2024)
```

### Database (`src/database.py`)

SQLite database for structured storage.

```python
from src.database import F1Database

db = F1Database()

# Insert race
race_id = db.insert_race(
    year=2024,
    round_number=1,
    event_name="Bahrain Grand Prix",
    country="Bahrain",
    location="Sakhir",
    event_date="2024-03-02"
)

# Insert driver
db.insert_driver(1, "VER", "Max Verstappen", "Red Bull Racing", 2024)

# Query races
races = db.get_all_races()

# Query predictions
predictions = db.get_predictions(race_id=race_id)
```

### Telemetry Handler (`src/telemetry_handler.py`)

JSON storage for telemetry data.

```python
from src.telemetry_handler import TelemetryHandler
import pandas as pd

handler = TelemetryHandler()

# Save telemetry
telemetry_df = pd.DataFrame({
    'Time': [0, 1, 2, 3],
    'Speed': [250, 260, 270, 280],
    'Throttle': [100, 100, 100, 100]
})
handler.save_telemetry(2024, "Bahrain", "VER", "R", telemetry_df)

# Load telemetry
telemetry, metadata = handler.load_telemetry(2024, "Bahrain", "VER", "R")

# List files
files = handler.list_available_telemetry()
```

### ML Models (`src/ml_models.py`)

Gradient Boosting and Random Forest ensemble.

```python
from src.ml_models import F1PredictionModel
import pandas as pd

model = F1PredictionModel()

# Prepare training data
data = pd.DataFrame({
    'driver_avg_position': [1.5, 3.2, 4.1],
    'driver_recent_form': [1.2, 3.5, 4.0],
    'team_avg_position': [1.5, 3.0, 4.5],
    'qualifying_position': [1, 3, 2],
    'grid_position': [1, 3, 2],
    'track_experience': [8, 10, 7],
    'points_before_race': [0, 0, 0],
    'race_position': [1, 3, 2]  # target
})

# Train models
X = model.prepare_features(data)
y = data['race_position']
model.train_ensemble(X, y)

# Make predictions
predictions = model.predict(X, model_type='ensemble')

# Get feature importance
importance = model.get_feature_importance('gradient_boosting')

# Save models
model.save_models('f1_race_model')

# Load models
model.load_models('f1_race_model')
```

## Streamlit Dashboard Pages

### 1. Home
- System overview
- Quick start guide
- Feature summary

### 2. Database Explorer
- View all tables
- Custom SQL queries
- Download data as CSV

### 3. Telemetry Viewer
- Browse telemetry files
- View JSON data
- Plot telemetry graphs

### 4. Model Predictions
- View stored predictions
- Filter by session type and model
- Visualize predictions

### 5. Feature Importance
- View feature importance
- Model explainability
- Interactive charts

## Jupyter Notebook Workflow

The notebook (`notebooks/f1_ml_pipeline.ipynb`) includes:

1. **Data Collection**: Fetch F1 data from FastF1
2. **Feature Engineering**: Create features for ML models
3. **Model Training**: Train Gradient Boosting and Random Forest
4. **Evaluation**: Assess model performance
5. **Feature Importance**: Analyze which features matter most
6. **Predictions**: Make predictions for current and 2026 seasons
7. **Storage**: Save models and predictions to database

## Offline Mode

Once data is cached:

1. **FastF1 Cache**: Located in `cache/` directory
2. **Database**: `f1_data.db` persists all structured data
3. **Telemetry**: JSON files in `telemetry_data/`
4. **Models**: Trained models in `models/`

No internet connection needed after initial data fetch!

## Advanced Usage

### Custom Feature Engineering

```python
# Add custom features to training data
data['driver_team_synergy'] = data['driver_avg_position'] * data['team_avg_position']
data['form_momentum'] = data['driver_recent_form'] - data['driver_avg_position']

# Train with custom features
model = F1PredictionModel()
X = model.prepare_features(data)
y = data['race_position']
model.train_ensemble(X, y)
```

### Model Tuning

```python
# Train with custom hyperparameters
model.train_gradient_boosting(
    X_train, y_train,
    n_estimators=200,
    learning_rate=0.05,
    max_depth=7
)

model.train_random_forest(
    X_train, y_train,
    n_estimators=150,
    max_depth=12,
    min_samples_split=3
)
```

### Batch Predictions

```python
# Make predictions for multiple races
races = [1, 2, 3, 4, 5]
all_predictions = []

for race in races:
    race_data = prepare_race_data(race)
    X = model.prepare_features(race_data)
    predictions = model.predict(X, model_type='ensemble')
    all_predictions.append(predictions)
```

## Troubleshooting

### Cache Issues
```bash
# Clear FastF1 cache
rm -rf cache/
```

### Database Reset
```bash
# Delete and recreate database
rm f1_data.db
python src/database.py
```

### Model Retraining
```bash
# Delete old models
rm -rf models/
# Run Jupyter notebook to retrain
```

## Performance Tips

1. **Cache Data**: Always cache F1 data for offline use
2. **Batch Operations**: Process multiple races together
3. **Feature Selection**: Use only relevant features
4. **Model Saving**: Save trained models to avoid retraining
5. **Database Indexing**: Query efficiently using race_id

## API Reference

See individual module docstrings for detailed API documentation:

```python
help(F1DataFetcher)
help(F1Database)
help(TelemetryHandler)
help(F1PredictionModel)
```

## Contributing

To add new features:
1. Follow existing code structure
2. Add tests for new functionality
3. Update documentation
4. Submit pull request

## License

MIT License
