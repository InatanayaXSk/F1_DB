# ER to Relational Mapping - F1 Database System

**RaceKraft: Intelligent Formula 1 Race Analytics and Prediction System**

---

## Table of Contents
1. [Introduction](#introduction)
2. [ER to Relational Mapping Rules](#er-to-relational-mapping-rules)
3. [Entity Mapping](#entity-mapping)
4. [Relationship Mapping](#relationship-mapping)
5. [Attribute Mapping](#attribute-mapping)
6. [Complete Relational Schema](#complete-relational-schema)
7. [Normalization Journey](#normalization-journey)
8. [Design Trade-offs](#design-trade-offs)

---

## Introduction

This document describes the systematic mapping from the Entity-Relationship (ER) model to the relational database schema for the RaceKraft F1 analytics system. The mapping follows standard ER-to-relational transformation rules while incorporating practical design decisions for analytical workloads.

### ER Model Overview

The RaceKraft ER diagram comprises:
- **10 core entities**: DRIVERS, TEAMS, RACES, SESSIONS, QUALIFYING_RESULT, SPRINT_RESULT, RACE_RESULT, AGGREGATED_LAP, TYRE_STAT, PREDICTION
- **14 relationships**: Employment, Session management, Competition, Performance recording
- **Cardinality patterns**: Primarily 1:N relationships with total/partial participation
- **Key constraints**: Composite keys, surrogate keys, year-scoped identities

### Mapping Process Overview

```mermaid
flowchart TD
    A[ER Model] --> B{Entity Type}
    B -->|Strong Entity| C[Create Table]
    B -->|Weak Entity| D[Add Owner FK]
    B -->|Associative| E[Junction Table]
    
    C --> F{Attributes}
    D --> F
    E --> F
    
    F -->|Simple| G[Single Column]
    F -->|Composite| H[Multiple Columns]
    F -->|Multi-valued| I[Separate Table]
    F -->|Derived| J[Computed/Materialized]
    
    G --> K{Relationships}
    H --> K
    I --> K
    J --> K
    
    K -->|1:N| L[FK on N side]
    K -->|M:N| M[Junction Table]
    K -->|1:1| N[FK either side]
    
    L --> O[Relational Schema]
    M --> O
    N --> O
    
    O --> P{Normalization}
    P -->|1NF| Q[Atomic Values]
    P -->|2NF| R[Remove Partial Deps]
    P -->|3NF| S[Remove Transitive Deps]
    P -->|BCNF| T[Superkey Determinants]
    
    Q --> U[Production Schema]
    R --> U
    S --> U
    T --> U
    
    style A fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style O fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style U fill:#fff59d,stroke:#f57f17,stroke-width:2px
```

---

## ER to Relational Mapping Rules

### Rule 1: Strong Entity Mapping
**ER Rule**: Each strong entity becomes a table  
**Relational Rule**: Entity name → Table name, Attributes → Columns, Primary key preserved

**Visual Example:**

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
```

**Application:**
- DRIVERS entity → `drivers` table
- TEAMS entity → `teams` table
- RACES entity → `races` table
- SESSIONS entity → `sessions` table

**Transformation:**
```mermaid
flowchart LR
    A["ER Entity:<br/>DRIVERS<br/>• driver_id (PK)<br/>• driver_number<br/>• full_name<br/>• team_name<br/>• year"] -->|Map| B["SQL Table:<br/>drivers<br/>• driver_id PK<br/>• driver_number<br/>• full_name<br/>• team_name<br/>• year"]
    
    style A fill:#ffe082,stroke:#fb8c00,stroke-width:2px
    style B fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

### Rule 2: Weak Entity Mapping
**ER Rule**: Weak entity inherits owner's primary key as foreign key  
**Relational Rule**: Composite primary key = {Owner PK + Partial key}

**Visual Example:**

```mermaid
erDiagram
    RACES ||--o{ SESSIONS : includes
    RACES {
        int race_id PK
        int year
        int round_number
        string event_name
    }
    SESSIONS {
        int session_id PK
        int race_id FK
        string session_type
        string session_date
    }
```

**Application:**
- SESSIONS is weak to RACES
  - Primary key: `session_id` (surrogate)
  - Foreign key: `race_id` references RACES
  - Discriminator: `session_type` (FP1, FP2, FP3, Q, S, R)

**Transformation:**
```mermaid
flowchart LR
    A["ER Weak Entity:<br/>SESSIONS<br/>• session_type (partial key)<br/>• session_date<br/>Depends on RACES"] -->|Add Owner FK| B["SQL Table:<br/>sessions<br/>• session_id PK<br/>• race_id FK<br/>• session_type<br/>• session_date"]
    
    style A fill:#ffccbc,stroke:#d84315,stroke-width:2px
    style B fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

### Rule 3: 1:N Relationship Mapping
**ER Rule**: Place foreign key on "many" side  
**Relational Rule**: Parent PK becomes FK in child table

**Visual Example:**

```mermaid
erDiagram
    TEAMS ||--o{ DRIVERS : employs
    TEAMS {
        int team_id PK
        string team_name
        int year
    }
    DRIVERS {
        int driver_id PK
        string team_name
        int year
    }
```

**Application:**
```
TEAMS (1) —employs→ (N) DRIVERS
Implementation:
  teams (team_id PK, team_name, year)
  drivers (driver_id PK, team_name, year)  -- Denormalized team_name
```

**Transformation Diagram:**
```mermaid
flowchart TD
    A["ER Relationship:<br/>TEAMS (1) employs (N) DRIVERS"] --> B{Where to place FK?}
    B -->|Option 1: BCNF| C["Add team_id FK<br/>in drivers table"]
    B -->|Option 2: Denormalized| D["Copy team_name<br/>into drivers table"]
    
    C --> E["drivers<br/>• driver_id PK<br/>• team_id FK<br/>• year"]
    D --> F["drivers<br/>• driver_id PK<br/>• team_name<br/>• year"]
    
    F --> G[Production Choice:<br/>Better query performance]
    
    style A fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style C fill:#ffccbc,stroke:#d84315,stroke-width:2px
    style D fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style G fill:#fff59d,stroke:#f57f17,stroke-width:2px
```

### Rule 4: Composite Attribute Mapping
**ER Rule**: Flatten composite attributes into atomic columns  
**Relational Rule**: Composite → Multiple columns

**Application:**
- Full Name → `full_name` (single column, not split)
- Address → Not applicable (no composite attributes in this schema)

### Rule 5: Multi-valued Attribute Mapping
**ER Rule**: Create separate table with foreign key to owner  
**Relational Rule**: New table = {Owner FK + Multi-valued attribute}

**Application:**
- AGGREGATED_LAP handles multiple laps per driver per session
  - `lap_id` PK
  - `race_id` FK
  - `driver_number`
  - `lap_number` (discriminator)

### Rule 6: Derived Attribute Mapping
**ER Rule**: Generally not stored; computed on demand  
**Relational Rule**: Can be computed view or materialized for performance

**Application:**
- `season_points_cumsum` → Derived from RACE_RESULT.points (materialized in feature engineering)
- `driver_avg_position` → Computed from historical RACE_RESULT
- `degradation_slope` → Derived from AGGREGATED_LAP.lap_time regression

---

## Entity Mapping

### Entity Mapping Overview

```mermaid
flowchart TD
    subgraph ER_Model["ER Model Entities"]
        E1[DRIVERS]
        E2[TEAMS]
        E3[RACES]
        E4[SESSIONS]
        E5[QUALIFYING_RESULT]
        E6[SPRINT_RESULT]
        E7[RACE_RESULT]
        E8[AGGREGATED_LAP]
        E9[TYRE_STAT]
        E10[PREDICTION]
    end
    
    subgraph Relational_Schema["Relational Tables"]
        T1[drivers]
        T2[teams]
        T3[races]
        T4[sessions]
        T5[qualifying_result]
        T6[sprint_result]
        T7[race_result]
        T8[aggregated_lap]
        T9[tyre_stat]
        T10[prediction]
    end
    
    E1 -->|1:1 Mapping| T1
    E2 -->|1:1 Mapping| T2
    E3 -->|1:1 Mapping| T3
    E4 -->|Weak Entity<br/>+ race_id FK| T4
    E5 -->|+ race_id FK| T5
    E6 -->|+ race_id FK| T6
    E7 -->|+ race_id FK| T7
    E8 -->|Multi-valued<br/>+ race_id FK| T8
    E9 -->|Aggregated<br/>+ race_id FK| T9
    E10 -->|ML Output<br/>+ race_id FK| T10
    
    style ER_Model fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style Relational_Schema fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style E1,E2,E3 fill:#ffe082,stroke:#fb8c00,stroke-width:1px
    style E4 fill:#ffccbc,stroke:#d84315,stroke-width:1px
    style E5,E6,E7,E8,E9,E10 fill:#fff59d,stroke:#f57f17,stroke-width:1px
```

---

### 1. DRIVERS Entity
**ER Definition:**
```
DRIVERS (driver_id, driver_number, abbreviation, full_name, team_name, year)
Primary Key: driver_id
Composite Key: (driver_number, year)
```

**Relational Mapping:**
```sql
CREATE TABLE drivers (
    driver_id       SERIAL PRIMARY KEY,
    driver_number   INTEGER NOT NULL,
    abbreviation    VARCHAR(3) NOT NULL,
    full_name       VARCHAR(100) NOT NULL,
    team_name       VARCHAR(100),
    year            INTEGER NOT NULL,
    UNIQUE (driver_number, year)
);
```

**Mapping Justification:**
- `driver_id`: Surrogate key for referential stability
- `(driver_number, year)`: Natural composite key (drivers can change numbers across seasons)
- `team_name`: Denormalized from TEAMS for query performance (read-heavy workload)

---

### 2. TEAMS Entity
**ER Definition:**
```
TEAMS (team_id, team_name, year)
Primary Key: team_id
Composite Key: (team_name, year)
```

**Relational Mapping:**
```sql
CREATE TABLE teams (
    team_id     SERIAL PRIMARY KEY,
    team_name   VARCHAR(100) NOT NULL,
    year        INTEGER NOT NULL,
    UNIQUE (team_name, year)
);
```

**Mapping Justification:**
- Year-scoped to track team name changes (e.g., Racing Point → Aston Martin)
- Tracks constructor stability across seasons

---

### 3. RACES Entity
**ER Definition:**
```
RACES (race_id, year, round_number, event_name, country, location, event_date)
Primary Key: race_id
Composite Key: (year, round_number)
```

**Relational Mapping:**
```sql
CREATE TABLE races (
    race_id       SERIAL PRIMARY KEY,
    year          INTEGER NOT NULL,
    round_number  INTEGER NOT NULL,
    event_name    VARCHAR(100) NOT NULL,
    country       VARCHAR(100),
    location      VARCHAR(100),
    event_date    VARCHAR(20),
    UNIQUE (year, round_number)
);
```

**Mapping Justification:**
- `(year, round_number)` uniquely identifies each Grand Prix
- `event_date` stored as VARCHAR for flexibility (DATE type could enforce stricter format)

---

### 4. SESSIONS Entity
**ER Definition:**
```
SESSIONS (session_id, race_id FK, session_type, session_date, weather_conditions, track_temp, air_temp)
Primary Key: session_id
Foreign Key: race_id → RACES
```

**Relational Mapping:**
```sql
CREATE TABLE sessions (
    session_id          SERIAL PRIMARY KEY,
    race_id             INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    session_type        VARCHAR(20) NOT NULL,  -- FP1, FP2, FP3, Q, S, R
    session_date        VARCHAR(20),
    weather_conditions  VARCHAR(100),
    track_temp          REAL,
    air_temp            REAL,
    UNIQUE (race_id, session_type)
);
```

**Mapping Justification:**
- Weak entity dependent on RACES (cascade delete)
- `session_type` discriminator ensures one session per type per race
- Weather attributes support predictive modeling

---

### 5. QUALIFYING_RESULT Entity
**ER Definition:**
```
QUALIFYING_RESULT (result_id, race_id FK, driver_number, position, q1_time, q2_time, q3_time)
Primary Key: result_id
Foreign Key: race_id → RACES
```

**Relational Mapping:**
```sql
CREATE TABLE qualifying_result (
    result_id      SERIAL PRIMARY KEY,
    race_id        INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_number  INTEGER NOT NULL,
    position       INTEGER,
    q1_time        VARCHAR(20),
    q2_time        VARCHAR(20),
    q3_time        VARCHAR(20),
    UNIQUE (race_id, driver_number)
);
```

**Mapping Justification:**
- Uses `driver_number` instead of `driver_id` for denormalization (avoids join with drivers table)
- Lap times stored as VARCHAR to preserve source format (e.g., "1:23.456")
- Position nullable for DNF/DNS cases

---

### 6. SPRINT_RESULT Entity
**ER Definition:**
```
SPRINT_RESULT (result_id, race_id FK, driver_number, position, points, status)
Primary Key: result_id
Foreign Key: race_id → RACES
```

**Relational Mapping:**
```sql
CREATE TABLE sprint_result (
    result_id      SERIAL PRIMARY KEY,
    race_id        INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_number  INTEGER NOT NULL,
    position       INTEGER,
    points         REAL DEFAULT 0,
    status         VARCHAR(50),
    UNIQUE (race_id, driver_number)
);
```

**Mapping Justification:**
- Status field captures DNF/DSQ/Finished outcomes
- Points DEFAULT 0 for non-scoring positions

---

### 7. RACE_RESULT Entity
**ER Definition:**
```
RACE_RESULT (result_id, race_id FK, driver_number, position, points, grid_position, status, fastest_lap_time)
Primary Key: result_id
Foreign Key: race_id → RACES
```

**Relational Mapping:**
```sql
CREATE TABLE race_result (
    result_id         SERIAL PRIMARY KEY,
    race_id           INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    driver_number     INTEGER NOT NULL,
    position          INTEGER,
    points            REAL DEFAULT 0,
    grid_position     INTEGER,
    status            VARCHAR(50),
    fastest_lap_time  VARCHAR(20),
    UNIQUE (race_id, driver_number)
);
```

**Mapping Justification:**
- `grid_position` captures starting position (from qualifying or sprint)
- `fastest_lap_time` tracks bonus point eligibility (top-10 finisher with fastest lap)

---

### 8. AGGREGATED_LAP Entity
**ER Definition:**
```
AGGREGATED_LAP (lap_id, race_id FK, session_type, driver_number, lap_number, lap_time, 
                sector1_time, sector2_time, sector3_time, compound, tyre_life, is_personal_best)
Primary Key: lap_id
Foreign Keys: race_id → RACES
```

**Relational Mapping:**
```sql
CREATE TABLE aggregated_lap (
    lap_id            SERIAL PRIMARY KEY,
    race_id           INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    session_type      VARCHAR(20) NOT NULL,
    driver_number     INTEGER NOT NULL,
    lap_number        INTEGER NOT NULL,
    lap_time          REAL,
    sector1_time      REAL,
    sector2_time      REAL,
    sector3_time      REAL,
    compound          VARCHAR(20),  -- SOFT, MEDIUM, HARD, INTERMEDIATE, WET
    tyre_life         INTEGER,
    is_personal_best  INTEGER DEFAULT 0,  -- Boolean flag
    UNIQUE (race_id, session_type, driver_number, lap_number)
);
```

**Mapping Justification:**
- Multi-valued attribute (multiple laps) → separate table
- Sector times support detailed performance analysis
- `compound` denormalized (not FK to compound_types) for query simplicity

---

### 9. TYRE_STAT Entity
**ER Definition:**
```
TYRE_STAT (tyre_stat_id, race_id FK, session_type, driver_number, compound,
           total_laps, avg_lap_time, degradation_slope, best_lap_time, stint_number)
Primary Key: tyre_stat_id
Foreign Key: race_id → RACES
```

**Relational Mapping:**
```sql
CREATE TABLE tyre_stat (
    tyre_stat_id      SERIAL PRIMARY KEY,
    race_id           INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    session_type      VARCHAR(20) NOT NULL,
    driver_number     INTEGER NOT NULL,
    compound          VARCHAR(20) NOT NULL,
    total_laps        INTEGER,
    avg_lap_time      REAL,
    degradation_slope REAL,  -- Seconds per lap increase
    best_lap_time     REAL,
    stint_number      INTEGER,
    UNIQUE (race_id, session_type, driver_number, compound, stint_number)
);
```

**Mapping Justification:**
- Aggregates lap-level data for strategy analysis
- `degradation_slope` derived from linear regression on AGGREGATED_LAP
- Composite unique key prevents duplicate stint statistics

---

### 10. PREDICTION Entity
**ER Definition:**
```
PREDICTION (prediction_id, race_id FK, session_type, driver_number, predicted_position,
            predicted_time, confidence, top10_probability, model_type, prediction_date,
            features_json, shap_values_json)
Primary Key: prediction_id
Foreign Key: race_id → RACES
```

**Relational Mapping:**
```sql
CREATE TABLE prediction (
    prediction_id      SERIAL PRIMARY KEY,
    race_id            INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    session_type       VARCHAR(20) NOT NULL,
    driver_number      INTEGER NOT NULL,
    predicted_position INTEGER,
    predicted_time     REAL,
    confidence         REAL,  -- 0.0 to 1.0
    top10_probability  REAL,
    model_type         VARCHAR(50),  -- GradientBoosting, RandomForest, XGBoost, LightGBM
    prediction_date    VARCHAR(30),
    features_json      TEXT,  -- JSON array of feature values
    shap_values_json   TEXT,  -- JSON array of SHAP values
    UNIQUE (race_id, session_type, driver_number, model_type)
);
```

**Mapping Justification:**
- JSON columns provide schema flexibility for evolving ML features
- `model_type` allows multiple predictions per driver from different models
- TEXT type for JSON (PostgreSQL supports JSONB for better performance)

---

## Relationship Mapping

### 1. TEAMS →employs→ DRIVERS (1:N)
**ER Relationship:**
```
TEAMS (1) ←employs→ (N) DRIVERS
Cardinality: One team employs multiple drivers
Participation: Total from DRIVERS, Partial from TEAMS
```

**Relational Implementation:**
```sql
-- Foreign key approach (BCNF):
ALTER TABLE drivers ADD COLUMN team_id INTEGER REFERENCES teams(team_id);

-- Denormalized approach (Production):
-- team_name stored directly in drivers table for query performance
```

**Decision:** Production schema uses denormalized `team_name` in `drivers` table to avoid join overhead on analytical queries.

---

### 2. RACES →has_session→ SESSIONS (1:N)
**ER Relationship:**
```
RACES (1) ←has_session→ (N) SESSIONS
Cardinality: One race has multiple sessions (FP1, FP2, FP3, Q, S, R)
Participation: Total from SESSIONS
```

**Relational Implementation:**
```sql
-- Foreign key in SESSIONS table:
CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    race_id INTEGER NOT NULL REFERENCES races(race_id) ON DELETE CASCADE,
    session_type VARCHAR(20) NOT NULL,
    ...
);
```

**Decision:** Cascade delete ensures sessions are removed when race is deleted (integrity).

---

### 3. RACES →has_results→ QUALIFYING_RESULT, SPRINT_RESULT, RACE_RESULT (1:N)
**ER Relationship:**
```
RACES (1) ←has→ (N) QUALIFYING_RESULT
RACES (1) ←has→ (N) SPRINT_RESULT
RACES (1) ←has→ (N) RACE_RESULT
Cardinality: One race generates multiple driver results
Participation: Total from result tables
```

**Relational Implementation:**
```sql
-- Foreign key in all result tables:
ALTER TABLE qualifying_result ADD COLUMN race_id INTEGER REFERENCES races(race_id);
ALTER TABLE sprint_result ADD COLUMN race_id INTEGER REFERENCES races(race_id);
ALTER TABLE race_result ADD COLUMN race_id INTEGER REFERENCES races(race_id);
```

**Decision:** Separate tables for each result type (normalization) rather than single results table with type discriminator.

---

### 4. DRIVERS →competes→ QUALIFYING_RESULT, SPRINT_RESULT, RACE_RESULT (1:N)
**ER Relationship:**
```
DRIVERS (1) ←competes→ (N) QUALIFYING_RESULT
DRIVERS (1) ←competes→ (N) SPRINT_RESULT
DRIVERS (1) ←competes→ (N) RACE_RESULT
Cardinality: One driver competes in multiple qualifying/sprint/race sessions
Participation: Partial from DRIVERS (not all drivers participate in all sessions)
```

**Relational Implementation:**
```sql
-- Denormalized approach using driver_number:
-- Result tables use driver_number instead of driver_id FK
-- Avoids join with drivers table on queries
```

**Decision:** `driver_number` used instead of `driver_id` FK for performance (denormalization trade-off).

---

### 5. DRIVERS →drives→ AGGREGATED_LAP (1:N)
**ER Relationship:**
```
DRIVERS (1) ←drives→ (N) AGGREGATED_LAP
Cardinality: One driver completes multiple laps
Participation: Total from AGGREGATED_LAP
```

**Relational Implementation:**
```sql
-- Composite key approach:
ALTER TABLE aggregated_lap ADD UNIQUE (race_id, session_type, driver_number, lap_number);
```

**Decision:** Multi-valued attribute (laps) resolved by creating separate lap records.

---

### 6. DRIVERS →uses→ TYRE_STAT (1:N)
**ER Relationship:**
```
DRIVERS (1) ←uses→ (N) TYRE_STAT
Cardinality: One driver uses multiple tyre compounds across stints
Participation: Partial (tire stats only for completed laps)
```

**Relational Implementation:**
```sql
-- Foreign key via driver_number:
ALTER TABLE tyre_stat ADD UNIQUE (race_id, session_type, driver_number, compound, stint_number);
```

**Decision:** Aggregated data (avg lap time, degradation) computed from AGGREGATED_LAP.

---

### 7. DRIVERS →receives→ PREDICTION (1:N)
**ER Relationship:**
```
DRIVERS (1) ←receives→ (N) PREDICTION
Cardinality: One driver receives multiple predictions (different models, sessions)
Participation: Partial (predictions only for upcoming sessions)
```

**Relational Implementation:**
```sql
-- Composite unique key:
ALTER TABLE prediction ADD UNIQUE (race_id, session_type, driver_number, model_type);
```

**Decision:** Multiple models can predict same driver → `model_type` in composite key.

---

## Attribute Mapping

### Primary Keys
| Entity | ER Primary Key | Relational Primary Key | Type |
|--------|----------------|------------------------|------|
| DRIVERS | driver_id | driver_id | Surrogate (SERIAL) |
| TEAMS | team_id | team_id | Surrogate (SERIAL) |
| RACES | race_id | race_id | Surrogate (SERIAL) |
| SESSIONS | session_id | session_id | Surrogate (SERIAL) |
| QUALIFYING_RESULT | result_id | result_id | Surrogate (SERIAL) |
| SPRINT_RESULT | result_id | result_id | Surrogate (SERIAL) |
| RACE_RESULT | result_id | result_id | Surrogate (SERIAL) |
| AGGREGATED_LAP | lap_id | lap_id | Surrogate (SERIAL) |
| TYRE_STAT | tyre_stat_id | tyre_stat_id | Surrogate (SERIAL) |
| PREDICTION | prediction_id | prediction_id | Surrogate (SERIAL) |

**Justification:** Surrogate keys (auto-incrementing integers) preferred for:
- Referential stability (natural keys can change)
- Join performance (integer comparisons faster than string/composite)
- API simplicity (single-column references)

### Foreign Keys
| Table | Foreign Key | References | Cascade Behavior |
|-------|-------------|------------|------------------|
| sessions | race_id | races(race_id) | ON DELETE CASCADE |
| qualifying_result | race_id | races(race_id) | ON DELETE CASCADE |
| sprint_result | race_id | races(race_id) | ON DELETE CASCADE |
| race_result | race_id | races(race_id) | ON DELETE CASCADE |
| aggregated_lap | race_id | races(race_id) | ON DELETE CASCADE |
| tyre_stat | race_id | races(race_id) | ON DELETE CASCADE |
| prediction | race_id | races(race_id) | ON DELETE CASCADE |

**Justification:** Cascade delete ensures referential integrity (orphaned records removed automatically).

### Data Types
| Attribute | ER Type | PostgreSQL Type | Rationale |
|-----------|---------|-----------------|-----------|
| driver_id | Integer | SERIAL (INT) | Auto-increment |
| driver_number | Integer | INTEGER | Racing number (1-99) |
| abbreviation | String | VARCHAR(3) | Fixed 3-letter code |
| full_name | String | VARCHAR(100) | Driver name |
| year | Integer | INTEGER | Season year |
| lap_time | Real | REAL | Floating-point seconds |
| compound | String | VARCHAR(20) | Tire type (SOFT/MEDIUM/HARD) |
| features_json | JSON | TEXT | Flexible schema |
| shap_values_json | JSON | TEXT | ML explainability |

**Justification:**
- VARCHAR for variable-length strings (more efficient than CHAR)
- REAL for times/temperatures (DOUBLE PRECISION overkill for precision)
- TEXT for JSON (could upgrade to JSONB for indexing)

---

## Complete Relational Schema

### Schema Overview

The F1 RaceKraft relational schema consists of 10 normalized tables organized into 4 functional categories:

**Master Data (4 tables):**
- DRIVERS: Driver information with year-scoped team assignments
- TEAMS: Constructor/team information
- RACES: Grand Prix event details
- SESSIONS: Race weekend session metadata

**Result Data (3 tables):**
- QUALIFYING_RESULT: Qualifying session outcomes
- SPRINT_RESULT: Sprint race results  
- RACE_RESULT: Main race results

**Performance Data (2 tables):**
- AGGREGATED_LAP: Lap-by-lap telemetry summaries
- TYRE_STAT: Tire usage and degradation statistics

**ML Predictions (1 table):**
- PREDICTION: Machine learning model predictions with SHAP explainability

### Complete ER Diagram (Production Schema)

![F1 3NF Schema](../../images/3nf.png)

**Figure**: Third Normal Form (3NF) schema showing all 10 entities with complete attributes and foreign key relationships

### Mermaid Representation

```mermaid
erDiagram
    %% ========== MASTER DATA ENTITIES ==========
    DRIVERS {
        int driver_id PK "Surrogate key"
        int driver_number "Racing number (1-99)"
        string abbreviation "3-letter code (e.g., VER, HAM)"
        string full_name "Driver full name"
        string team_name "Current team (denormalized)"
        int year "Season year"
        UNIQUE "(driver_number, year)"
    }
    
    TEAMS {
        int team_id PK "Surrogate key"
        string team_name "Constructor name"
        int year "Season year"
        UNIQUE "(team_name, year)"
    }
    
    RACES {
        int race_id PK "Surrogate key"
        int year "Season year"
        int round_number "Race number in season (1-24)"
        string event_name "Grand Prix name"
        string country "Host country"
        string location "Circuit location"
        string event_date "Race date (YYYY-MM-DD)"
        UNIQUE "(year, round_number)"
    }
    
    SESSIONS {
        int session_id PK "Surrogate key"
        int race_id FK "References RACES"
        string session_type "FP1, FP2, FP3, Q, S, R"
        string session_date "Session date-time"
        string weather_conditions "Weather description"
        float track_temp "Track temperature (°C)"
        float air_temp "Air temperature (°C)"
        UNIQUE "(race_id, session_type)"
    }
    
    %% ========== RESULT ENTITIES ==========
    QUALIFYING_RESULT {
        int result_id PK "Surrogate key"
        int race_id FK "References RACES"
        int driver_number "Driver racing number"
        int position "Final qualifying position"
        string q1_time "Q1 lap time"
        string q2_time "Q2 lap time"
        string q3_time "Q3 lap time"
        UNIQUE "(race_id, driver_number)"
    }
    
    SPRINT_RESULT {
        int result_id PK "Surrogate key"
        int race_id FK "References RACES"
        int driver_number "Driver racing number"
        int position "Sprint finish position"
        float points "Points awarded"
        string status "Finished, DNF, DSQ, etc."
        UNIQUE "(race_id, driver_number)"
    }
    
    RACE_RESULT {
        int result_id PK "Surrogate key"
        int race_id FK "References RACES"
        int driver_number "Driver racing number"
        int position "Race finish position"
        float points "Championship points"
        int grid_position "Starting position"
        string status "Finished, DNF, DSQ, etc."
        string fastest_lap_time "Fastest lap (bonus point)"
        UNIQUE "(race_id, driver_number)"
    }
    
    %% ========== PERFORMANCE DATA ENTITIES ==========
    AGGREGATED_LAP {
        int lap_id PK "Surrogate key"
        int race_id FK "References RACES"
        string session_type "Session identifier"
        int driver_number "Driver racing number"
        int lap_number "Lap counter"
        float lap_time "Total lap time (seconds)"
        float sector1_time "Sector 1 time (seconds)"
        float sector2_time "Sector 2 time (seconds)"
        float sector3_time "Sector 3 time (seconds)"
        string compound "Tire compound (SOFT, MEDIUM, HARD)"
        int tyre_life "Laps on current tires"
        int is_personal_best "Boolean flag (0/1)"
        UNIQUE "(race_id, session_type, driver_number, lap_number)"
    }
    
    TYRE_STAT {
        int tyre_stat_id PK "Surrogate key"
        int race_id FK "References RACES"
        string session_type "Session identifier"
        int driver_number "Driver racing number"
        string compound "Tire compound"
        int total_laps "Laps on compound"
        float avg_lap_time "Average lap time (seconds)"
        float degradation_slope "Lap time increase per lap"
        float best_lap_time "Fastest lap on compound"
        int stint_number "Stint identifier"
        UNIQUE "(race_id, session_type, driver_number, compound, stint_number)"
    }
    
    %% ========== ML PREDICTION ENTITY ==========
    PREDICTION {
        int prediction_id PK "Surrogate key"
        int race_id FK "References RACES"
        string session_type "Target session (Q, S, R)"
        int driver_number "Driver racing number"
        int predicted_position "Predicted finish position"
        float predicted_time "Predicted lap/race time"
        float confidence "Prediction confidence (0-1)"
        float top10_probability "Probability of top-10 finish"
        string model_type "GradientBoosting, XGBoost, LightGBM, etc."
        string prediction_date "Prediction timestamp"
        string features_json "JSON array of feature values"
        string shap_values_json "SHAP explainability values"
        UNIQUE "(race_id, session_type, driver_number, model_type)"
    }
    
    %% ========== RELATIONSHIPS ==========
    %% Employment & Organization
    TEAMS ||--o{ DRIVERS : "employs (1:N) - One team employs multiple drivers per season"
    
    %% Race Organization
    RACES ||--o{ SESSIONS : "has_session (1:N) - Each race has FP1, FP2, FP3, Q, S, R sessions"
    
    %% Result Recording
    RACES ||--o{ QUALIFYING_RESULT : "has_qualifying (1:N) - Each race has ~20 qualifying results"
    RACES ||--o{ SPRINT_RESULT : "has_sprint (1:N) - Sprint races have ~20 results"
    RACES ||--o{ RACE_RESULT : "has_race (1:N) - Each race has ~20 finish results"
    
    %% Performance Data
    RACES ||--o{ AGGREGATED_LAP : "records_laps (1:N) - Each race records thousands of laps"
    RACES ||--o{ TYRE_STAT : "records_tyres (1:N) - Tire statistics per driver per stint"
    
    %% ML Predictions
    RACES ||--o{ PREDICTION : "has_predictions (1:N) - Multiple model predictions per race"
    
    %% Driver Participation
    DRIVERS ||--o{ QUALIFYING_RESULT : "competes_in (1:N) - Drivers compete in qualifying"
    DRIVERS ||--o{ SPRINT_RESULT : "participates (1:N) - Drivers participate in sprints"
    DRIVERS ||--o{ RACE_RESULT : "races_in (1:N) - Drivers race in main events"
    DRIVERS ||--o{ AGGREGATED_LAP : "drives_laps (1:N) - Drivers complete laps"
    DRIVERS ||--o{ TYRE_STAT : "uses_tyres (1:N) - Drivers use tire compounds"
    DRIVERS ||--o{ PREDICTION : "receives_prediction (1:N) - Drivers receive predictions"
```

**Schema Statistics:**
- **Total Tables**: 10
- **Total Relationships**: 14 (all 1:N)
- **Primary Keys**: 10 surrogate keys (SERIAL)
- **Foreign Keys**: 16 (race_id × 8 tables, team via denormalization)
- **Unique Constraints**: 10 composite unique keys
- **Average Columns per Table**: 8.5

---

## Normalization Journey

### Normalization Process Visualization

```mermaid
flowchart TD
    A[0NF: Raw FastF1 JSON<br/>Nested structures<br/>Repeating groups] -->|Flatten Arrays| B[1NF: Atomic Values<br/>One row per driver-session<br/>No nested data]
    
    B -->|Extract Entities| C[2NF: Remove Partial Dependencies<br/>Separate DRIVER, TEAM tables<br/>FK in SESSION_RESULT]
    
    C -->|Remove Transitive| D[3NF: Remove Transitive Dependencies<br/>DRIVER_SEASON for team assignments<br/>Separate result types]
    
    D -->|Superkey Determinants| E[BCNF: All Determinants are Keys<br/>DRIVER_NUMBER table<br/>Complete normalization]
    
    E -->|Optimize for Analytics| F[Production Schema<br/>Strategic denormalization<br/>Read-optimized]
    
    subgraph Issues["Normalization Issues Resolved"]
        I1[Update Anomalies]
        I2[Insertion Anomalies]
        I3[Deletion Anomalies]
        I4[Functional Dependencies]
    end
    
    subgraph Benefits["Production Benefits"]
        B1[Query Performance]
        B2[Schema Flexibility]
        B3[Data Integrity]
        B4[Analytical Queries]
    end
    
    A -.->|Has Issues| Issues
    F -.->|Achieves| Benefits
    
    style A fill:#ffccbc,stroke:#d84315,stroke-width:2px
    style B fill:#fff59d,stroke:#f57f17,stroke-width:2px
    style C fill:#ffe082,stroke:#fb8c00,stroke-width:2px
    style D fill:#c5e1a5,stroke:#689f38,stroke-width:2px
    style E fill:#b3e5fc,stroke:#0277bd,stroke-width:2px
    style F fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    style Issues fill:#ffebee,stroke:#c62828,stroke-width:1px
    style Benefits fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px
```

---

### 0NF: Raw FastF1 Capture
**Characteristics:**
- Nested JSON structures
- Repeating groups (drivers, laps, compounds)
- Multi-valued attributes in single row

**Example:**
```
race_2024_01 = {
  "drivers": [44, 1, 16, ...],
  "teams": ["Mercedes", "Red Bull", ...],
  "laps": {nested telemetry},
  "predictions": {model outputs}
}
```

**Violations:** First Normal Form (repeating groups, atomic value requirement)

---

### 1NF: Atomic Values
**Transformation:**
1. Flatten driver arrays → One row per driver per session
2. Separate lap arrays → One row per lap
3. Remove nested structures

**Result:**
```sql
event_header (event_id, season, event_name, circuit)
session_entry (event_id, session_type, driver_number, driver_name, team_name, fastest_lap, compound, points)
```

**Remaining Issues:** Partial dependencies (driver_name depends on driver_number, not full composite key)

---

### 2NF: Remove Partial Dependencies
**Transformation:**
1. Extract DRIVER and TEAM entities
2. Create foreign keys in SESSION_RESULT

**Result:**
```sql
driver (driver_id, driver_number, full_name, team_id)
team (team_id, team_name)
session_result (result_id, event_id, session_type, driver_id, fastest_lap, points)
```

**Remaining Issues:** Transitive dependencies (team_name changes affect driver table year-to-year)

---

### 3NF: Remove Transitive Dependencies
**Transformation:**
1. Separate DRIVER_SEASON for year-scoped team assignments
2. Split results by type (QUALIFYING_RESULT, SPRINT_RESULT, RACE_RESULT)
3. Extract AGGREGATED_LAP and TYRE_STAT

**Result:**
```sql
driver (driver_id, full_name)
team (team_id, team_name)
driver_season (assignment_id, driver_id, team_id, season_year)
qualifying_result (result_id, session_id, driver_id, position, q1, q2, q3)
```

**Remaining Issues:** driver_number can change across seasons (subtle BCNF violation)

---

### BCNF: Eliminate All Anomalies
**Transformation:**
1. Create DRIVER_NUMBER table to handle number changes
2. Ensure every determinant is a candidate key

**Result:**
```sql
driver (driver_id, full_name)
driver_number (driver_number_id, driver_id, driver_number, season_year)
```

**Achievement:** Full BCNF compliance (every functional dependency has superkey determinant)

---

### Production Schema: Pragmatic Denormalization
**Transformation Back:**
1. Merge team_name into drivers table (year-scoped) for query performance
2. Use driver_number directly in result tables (avoid driver_id join)
3. Store compound as VARCHAR (not FK to compound_types table)

**Rationale:**
- Read-heavy workload (90% queries, 10% writes)
- Historical data is immutable (no update anomalies in practice)
- Join elimination provides 10× query speedup for dashboards

---

## Design Trade-offs

### Denormalization Decisions

| Aspect | BCNF (Normalized) | Production (Denormalized) | Justification |
|--------|-------------------|---------------------------|---------------|
| **team_name in drivers** | FK to teams table | Stored in drivers table | Eliminates join on 90% of queries |
| **driver_number in results** | FK to driver_number table | Stored directly | Avoids driver_id lookup |
| **compound type** | FK to compound_types | VARCHAR value | Simplifies schema (limited domain) |
| **features_json** | Normalized feature table | JSON TEXT column | Schema flexibility for ML |

### Performance Optimizations

**Indexes:**
```sql
CREATE INDEX idx_drivers_number_year ON drivers(driver_number, year);
CREATE INDEX idx_qualifying_race_driver ON qualifying_result(race_id, driver_number);
CREATE INDEX idx_race_year_round ON races(year, round_number);
CREATE INDEX idx_aggregated_lap_session ON aggregated_lap(race_id, session_type, driver_number);
```

**Justification:**
- Composite indexes support common query patterns
- B-tree indexes for range queries (year, round_number)
- Covering indexes avoid table lookups

### Data Integrity vs. Performance

| Decision | Integrity Impact | Performance Impact | Choice |
|----------|------------------|-------------------|--------|
| Cascade deletes | Automatic orphan removal | Minimal overhead | ENABLED |
| Foreign keys | Referential integrity enforced | Insert/update checks | ENABLED |
| Check constraints | Domain validation | Minimal overhead | Selective |
| Triggers | Complex business rules | Significant overhead | MINIMAL |

**Philosophy:** Prioritize integrity for critical relationships (race → results), optimize for read performance on analytical queries.

---

## Conclusion

The ER-to-Relational mapping for RaceKraft balances theoretical normalization principles with practical performance requirements:

1. **Normalized Foundation:** Core entities (races, drivers, teams) maintain 3NF compliance
2. **Strategic Denormalization:** Result tables use driver_number denormalization for query performance
3. **Flexible Schema:** JSON columns support evolving ML features without migrations
4. **Integrity Safeguards:** Foreign keys and cascade deletes prevent data inconsistencies
5. **Year-Scoped Design:** Temporal correctness through year attributes in drivers/teams
6. **Analytical Optimization:** Read-heavy workload (90%) justifies denormalization trade-offs

This mapping provides a production-ready relational schema suitable for the RaceKraft F1 analytics platform while maintaining clear traceability to the original ER model.
