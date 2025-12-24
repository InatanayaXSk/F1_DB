# Data Flow and Normalization Overview

## Data Flow Diagrams

### Level 1 — Platform Context

```mermaid
flowchart TD
    subgraph External_Sources
        A[FastF1 API]
    end
    subgraph Core_Platform
        P1((Data Fetcher))
        P2((ML Pipeline))
        P3((Streamlit Dashboard))
    end
    subgraph Data_Stores
        D1[(Redis Cache)]
        D2[(PostgreSQL Warehouse)]
        D3[(Telemetry JSON Store)]
        D4[(Model Registry)]
    end
    U[Analyst User]

    A -->|Sessions, timing, metadata| P1
    P1 -->|Cached session packets| D1
    P1 -->|Normalized tables| D2
    P1 -->|Telemetry snapshots| D3
    D2 -->|Training data, historical labels| P2
    D3 -->|Lap traces| P2
    P2 -->|Predictions, feature importances| D2
    P2 -->|Trained artifacts| D4
    D4 -->|Inference models| P3
    D2 -->|Results, predictions| P3
    D3 -->|Telemetry laps| P3
    P3 -->|Visual insights| U
    U -->|Filters, scenario questions| P3
```

The level 1 diagram frames the entire platform: FastF1 exposes time-series data, [src/data_fetcher.py](src/data_fetcher.py) centralizes ingestion, three storage mediums persist different shapes of data, and both the ML pipeline and Streamlit dashboard read from the stores while feeding insights back to analysts.

### Level 2 — Data Fetcher Decomposition

```mermaid
flowchart TD
    A[FastF1 API]
    P1{{Request Session Data}}
    P2{{Normalize and Validate}}
    P3{{Distribute Storage}}
    D1[(Redis Cache)]
    D2[(PostgreSQL Warehouse)]
    D3[(Telemetry Store)]
    C1((ML Pipeline))
    C2((Streamlit App))

    A -->|Session metadata, timing packets| P1
    P1 -->|Raw packets| P2
    P2 -->|Clean session frame| P3
    P3 -->|Session cache keys| D1
    P3 -->|Structured tables| D2
    P3 -->|Lap JSON bundles| D3
    D1 -->|Warm cache hits| P1
    D2 -->|Historical datasets| C1
    D3 -->|Telemetry slices| C1
    D2 -->|Leaderboards, predictions| C2
    D3 -->|Lap overlays| C2
```

Level 2 breaks the ingestion process into request, normalization, and persistence steps while emphasizing that Redis accelerates replays and both downstream consumers reuse the curated outputs.

### Level 3 — ML Pipeline Decomposition

```mermaid
flowchart TD
    D2[(PostgreSQL Warehouse)]
    D3[(Telemetry Store)]
    F1{{Feature Engineering}}
    F2{{Model Training}}
    F3{{Evaluation and Selection}}
    F4{{Batch Prediction}}
    D4[(Model Registry)]
    D5[(SHAP Archive)]
    UI((Streamlit App))
    NB((Jupyter Notebook))

    D2 --> F1
    D3 --> F1
    F1 -->|Engineered features| F2
    F2 -->|Candidate estimators| F3
    F3 -->|Champion models| D4
    F3 --> F4
    D4 -->|Final models| F4
    F4 -->|Predicted grids| D2
    F4 -->|Explanation payloads| D5
    D2 --> UI
    D4 --> UI
    D5 --> UI
    D2 --> NB
    D4 --> NB
```

The level 3 view zooms in on the ML notebook and automation path: relational data and telemetry power feature creation, models are trained and scored, validated artifacts are versioned, and predictions plus explainability outputs feed both the analytical notebook and the live dashboard.

## Normalization Journey

The FastF1 feed arrives as nested telemetry structures. The project normalizes those records through successive stages before loading the production schema.

### Actual Raw Capture (0NF Baseline)

```mermaid
erDiagram
    RAW_FASTF1_CAPTURE {
        int season_year
        int round_number
        string event_name
        string circuit_name
        string session_bundle "FP1|FP2|Qualifying|Race"
        string driver_array "[44, 1, 16, ...]"
        string team_array "[Mercedes, Red Bull, ...]"
        string lap_packets "Nested lap-by-lap telemetry"
        string tyre_usage "Compound-lap pairs"
        string model_predictions "Serialized JSON"
    }
```

The initial capture mirrors the FastF1 bundle: multi-valued arrays mix driver, team, laps, and predictions inside a single record, violating First Normal Form because repeating groups and nested structures coexist in one row.

### First Normal Form (1NF)

```mermaid
erDiagram
    EVENT_HEADER {
        int event_id PK
        int season_year
        int round_number
        string event_name
        string circuit_name
    }

    SESSION_ENTRY {
        int event_id FK
        string session_type
        int driver_number
        string driver_name
        string team_name
        float fastest_lap
        string tyre_compound
        float points_awarded
    }

    EVENT_HEADER ||--o{ SESSION_ENTRY : contains
```

The 1NF stage flattens repeating groups so every session-driver combination is a separate row. However, attributes such as driver_name and team_name still depend only on part of the composite key (event_id, session_type, driver_number), leaving partial dependency issues for 2NF.

### Second Normal Form (2NF)

```mermaid
erDiagram
    EVENT {
        int event_id PK
        int season_year
        int round_number
        string event_name
        string circuit_name
    }

    SESSION_RESULT {
        int result_id PK
        int event_id FK
        string session_type
        int driver_id FK
        float fastest_lap
        float points_awarded
        string status
    }

    DRIVER {
        int driver_id PK
        int driver_number
        string full_name
        int team_id FK
    }

    TEAM {
        int team_id PK
        string team_name
    }

    EVENT ||--o{ SESSION_RESULT : includes
    DRIVER ||--o{ SESSION_RESULT : competes
    TEAM ||--o{ DRIVER : employs
```

By isolating DRIVER and TEAM, every non-key attribute in SESSION_RESULT depends on the full primary key, eliminating partial dependencies. Team details are now referenced through surrogate keys, yet TEAM still carries year-specific context inside its rows, creating a transitive dependency.

### Third Normal Form (3NF)

```mermaid
erDiagram
    RACE {
        int race_id PK
        int season_year
        int round_number
        string event_name
        string country
        string location
        string event_date
    }

    SESSION {
        int session_id PK
        int race_id FK
        string session_type
        string session_date
        string weather_conditions
        float track_temp
        float air_temp
    }

    TEAM {
        int team_id PK
        string team_name
    }

    DRIVER {
        int driver_id PK
        int driver_number
        string full_name
    }

    DRIVER_SEASON {
        int assignment_id PK
        int driver_id FK
        int team_id FK
        int season_year
    }

    QUALIFYING_RESULT {
        int result_id PK
        int session_id FK
        int driver_id FK
        int position
        string q1_time
        string q2_time
        string q3_time
    }

    SPRINT_RESULT {
        int result_id PK
        int session_id FK
        int driver_id FK
        int position
        float points
        string status
    }

    RACE_RESULT {
        int result_id PK
        int session_id FK
        int driver_id FK
        int position
        float points
        int grid_position
        string status
        string fastest_lap_time
    }

    AGGREGATED_LAP {
        int lap_id PK
        int session_id FK
        int driver_id FK
        int lap_number
        float lap_time
        float sector1_time
        float sector2_time
        float sector3_time
        string compound
        int tyre_life
        int is_personal_best
    }

    TYRE_STAT {
        int tyre_stat_id PK
        int session_id FK
        int driver_id FK
        string compound
        int stint_number
        int total_laps
        float avg_lap_time
        float degradation_slope
        float best_lap_time
    }

    PREDICTION {
        int prediction_id PK
        int session_id FK
        int driver_id FK
        string model_type
        int predicted_position
        float predicted_time
        float confidence
        float top10_probability
        string features_json
        string shap_values_json
    }

    RACE ||--o{ SESSION : includes
    SESSION ||--o{ QUALIFYING_RESULT : records
    SESSION ||--o{ SPRINT_RESULT : records
    SESSION ||--o{ RACE_RESULT : records
    SESSION ||--o{ AGGREGATED_LAP : logs
    SESSION ||--o{ TYRE_STAT : aggregates
    SESSION ||--o{ PREDICTION : forecasts
    DRIVER ||--o{ QUALIFYING_RESULT : competes
    DRIVER ||--o{ SPRINT_RESULT : competes
    DRIVER ||--o{ RACE_RESULT : competes
    DRIVER ||--o{ AGGREGATED_LAP : drives
    DRIVER ||--o{ TYRE_STAT : uses
    DRIVER ||--o{ PREDICTION : receives
    TEAM ||--o{ DRIVER_SEASON : assigns
    DRIVER ||--o{ DRIVER_SEASON : signs
```

The 3NF model removes transitive dependencies by splitting driver-team assignments into DRIVER_SEASON, isolating sessions, and distributing telemetry, tyre, and prediction facts into purpose-built entities. Every non-key attribute depends solely on its primary key.

### Actual Operational Schema (Production Alignment)

```mermaid
erDiagram
    DRIVERS {
        int driver_id PK
        int driver_number
        string abbreviation
        string full_name
        string team_name
        int year
    }

    TEAMS {
        int team_id PK
        string team_name
        int year
    }

    RACES {
        int race_id PK
        int year
        int round_number
        string event_name
        string country
        string location
        string event_date
    }

    SESSIONS {
        int session_id PK
        int race_id FK
        string session_type
        string session_date
        string weather_conditions
        float track_temp
        float air_temp
    }

    QUALIFYING_RESULT {
        int result_id PK
        int race_id FK
        int driver_number
        int position
        string q1_time
        string q2_time
        string q3_time
    }

    SPRINT_RESULT {
        int result_id PK
        int race_id FK
        int driver_number
        int position
        float points
        string status
    }

    RACE_RESULT {
        int result_id PK
        int race_id FK
        int driver_number
        int position
        float points
        int grid_position
        string status
        string fastest_lap_time
    }

    AGGREGATED_LAP {
        int lap_id PK
        int race_id FK
        string session_type
        int driver_number
        int lap_number
        float lap_time
        float sector1_time
        float sector2_time
        float sector3_time
        string compound
        int tyre_life
        int is_personal_best
    }

    TYRE_STAT {
        int tyre_stat_id PK
        int race_id FK
        string session_type
        int driver_number
        string compound
        int total_laps
        float avg_lap_time
        float degradation_slope
        float best_lap_time
        int stint_number
    }

    PREDICTION {
        int prediction_id PK
        int race_id FK
        string session_type
        int driver_number
        int predicted_position
        float predicted_time
        float confidence
        float top10_probability
        string model_type
        string prediction_date
        string features_json
        string shap_values_json
    }

    TEAMS ||--o{ DRIVERS : employs
    RACES ||--o{ SESSIONS : has
    RACES ||--o{ QUALIFYING_RESULT : has
    RACES ||--o{ SPRINT_RESULT : has
    RACES ||--o{ RACE_RESULT : has
    RACES ||--o{ PREDICTION : has
    RACES ||--o{ AGGREGATED_LAP : records
    RACES ||--o{ TYRE_STAT : records
    DRIVERS ||--o{ QUALIFYING_RESULT : competes
    DRIVERS ||--o{ SPRINT_RESULT : competes
    DRIVERS ||--o{ RACE_RESULT : competes
    DRIVERS ||--o{ PREDICTION : receives
    DRIVERS ||--o{ AGGREGATED_LAP : drives
    DRIVERS ||--o{ TYRE_STAT : uses
```

The deployed database mirrors the entity set described in [docs/dgm.md](docs/dgm.md). Driver rows intentionally retain the team_name for the given season to streamline analytical queries, while race-centric tables separate qualifying, sprint, race, telemetry, tyre, and prediction facts without duplicating session metadata.
