# F1 Prediction System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    F1 PREDICTION SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   FastF1 API         │────────▶│   Data Fetcher       │
│   (Official F1 Data) │         │   (data_fetcher.py)  │
└──────────────────────┘         └──────────┬───────────┘
                                            │
                                            │ Cache
                                            ▼
                        ┌───────────────────────────────┐
                        │      Redis Cache Server       │
                        │   (Fast In-Memory Caching)    │
                        └───────────┬───────────────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                     ▼              ▼              ▼
         ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
         │PostgreSQL Database│  │ JSON Files   │  │  ML Models   │
         │  (database.py)   │  │ (telemetry   │  │ (ml_models   │
         │                  │  │  _handler.py)│  │  .py)        │
         │ • Drivers        │  │              │  │              │
         │ • Teams          │  │ • Telemetry  │  │ • Gradient   │
         │ • Races          │  │ • Lap Data   │  │   Boosting   │
         │ • Results        │  │ • Metadata   │  │ • Random     │
         │ • Predictions    │  │              │  │   Forest     │
         └────────┬─────────┘  └──────┬───────┘  └──────┬───────┘
                  │                   │                  │
                  └───────────────────┼──────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │  Jupyter Notebook       │
                        │  (f1_ml_pipeline.ipynb) │
                        │                         │
                        │  • Feature Engineering  │
                        │  • Model Training       │
                        │  • Evaluation           │
                        │  • Predictions          │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │  Streamlit Dashboard    │
                        │  (streamlit_app.py)     │
                        │                         │
                        │  • Database Explorer    │
                        │  • Telemetry Viewer     │
                        │  • Model Predictions    │
                        │  • Feature Importance   │
                        └─────────────────────────┘
```

## Data Flow

1. **Data Collection**
   - FastF1 API → Data Fetcher → Cache
   - Historical data cached for offline use

2. **Storage**
   - Structured data → PostgreSQL Database
   - Telemetry data → JSON Files
   - Trained models → Pickle Files

3. **Machine Learning**
   - Training data from database
   - Feature engineering
   - Ensemble training (GB + RF)
   - Model evaluation

4. **Predictions**
   - Load trained models
   - Process new data
   - Generate predictions
   - Store in database

5. **Visualization**
   - Streamlit dashboard
   - Interactive exploration
   - Feature importance analysis

## Key Features

### High-Performance Caching ✓
Once data is cached:
- FastF1 cache: Redis (in-memory)
- Database: PostgreSQL
- Telemetry: `telemetry_data/`
- Models: `models/`

### Prediction Types
- Qualifying positions
- Sprint race results
- Main race results
- 2026 season forecasts

### ML Models
- **Gradient Boosting**: Complex pattern recognition
- **Random Forest**: Robust predictions with feature importance
- **Ensemble**: Average of both models for best accuracy

### Explainability
- Feature importance rankings
- Model confidence scores
- Interactive visualizations

## Technology Stack

- **Data**: FastF1, Pandas, NumPy
- **Storage**: PostgreSQL, Redis, JSON
- **ML**: Scikit-learn (GradientBoosting, RandomForest)
- **Visualization**: Streamlit, Plotly, Matplotlib, Seaborn
- **Notebook**: Jupyter

## Module Dependencies

```
data_fetcher.py
    ├─ fastf1
    ├─ redis
    └─ pandas

database.py
    ├─ psycopg2
    └─ pandas

telemetry_handler.py
    ├─ json
    └─ pandas

ml_models.py
    ├─ sklearn.ensemble
    ├─ sklearn.preprocessing
    └─ pickle

streamlit_app.py
    ├─ streamlit
    ├─ plotly
    ├─ database
    ├─ telemetry_handler
    └─ ml_models
```
