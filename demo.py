"""
Demo script to showcase F1 Prediction System capabilities
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import F1Database
from telemetry_handler import TelemetryHandler
from ml_models import F1PredictionModel
import pandas as pd
import numpy as np


def main():
    print("\n" + "="*60)
    print("F1 PREDICTION SYSTEM - DEMO")
    print("="*60)
    
    # 1. Database Demo
    print("\n1. DATABASE OPERATIONS")
    print("-" * 60)
    db = F1Database()
    
    # Insert sample race data
    race_id = db.insert_race(
        year=2024,
        round_number=1,
        event_name="Bahrain Grand Prix",
        country="Bahrain",
        location="Sakhir",
        event_date="2024-03-02"
    )
    print(f"✓ Created race entry with ID: {race_id}")
    
    # Insert sample drivers
    drivers = [
        (1, "VER", "Max Verstappen", "Red Bull Racing", 2024),
        (44, "HAM", "Lewis Hamilton", "Mercedes", 2024),
        (16, "LEC", "Charles Leclerc", "Ferrari", 2024),
        (4, "NOR", "Lando Norris", "McLaren", 2024),
        (11, "PER", "Sergio Perez", "Red Bull Racing", 2024),
    ]
    
    for driver in drivers:
        db.insert_driver(*driver)
    print(f"✓ Inserted {len(drivers)} drivers")
    
    # 2. Telemetry Demo
    print("\n2. TELEMETRY STORAGE")
    print("-" * 60)
    handler = TelemetryHandler()
    
    # Create sample telemetry
    sample_telemetry = pd.DataFrame({
        'Time': np.linspace(0, 90, 100),
        'Speed': np.sin(np.linspace(0, 10, 100)) * 50 + 250,
        'Throttle': np.random.uniform(80, 100, 100),
        'Brake': np.random.uniform(0, 10, 100),
        'RPM': np.random.uniform(10000, 13000, 100),
    })
    
    handler.save_telemetry(2024, "Bahrain", "VER", "Q", sample_telemetry)
    handler.save_telemetry(2024, "Bahrain", "HAM", "Q", sample_telemetry)
    
    summary = handler.get_telemetry_summary()
    print(f"✓ Total telemetry files: {summary['total_files']}")
    
    # 3. ML Model Demo
    print("\n3. MACHINE LEARNING PREDICTIONS")
    print("-" * 60)
    
    # Create training data
    np.random.seed(42)
    training_data = pd.DataFrame({
        'driver_avg_position': np.random.uniform(1, 20, 200),
        'driver_recent_form': np.random.uniform(1, 20, 200),
        'team_avg_position': np.random.uniform(1, 10, 200),
        'grid_position': np.random.randint(1, 21, 200),
        'qualifying_position': np.random.randint(1, 21, 200),
        'track_experience': np.random.randint(0, 10, 200),
        'points_before_race': np.random.uniform(0, 400, 200),
    })
    
    training_data['race_position'] = (
        0.35 * training_data['qualifying_position'] +
        0.25 * training_data['driver_avg_position'] +
        0.20 * training_data['team_avg_position'] +
        np.random.normal(0, 2, 200)
    ).clip(1, 20)
    
    # Train model
    model = F1PredictionModel()
    X = model.prepare_features(training_data)
    y = training_data['race_position']
    
    print("Training models...")
    model.train_ensemble(X, y, test_size=0.2)
    
    # Make predictions for 2024 Bahrain GP
    print("\n4. PREDICTIONS FOR 2024 BAHRAIN GP")
    print("-" * 60)
    
    prediction_data = pd.DataFrame({
        'driver_number': [1, 44, 16, 4, 11],
        'driver_name': ['VER', 'HAM', 'LEC', 'NOR', 'PER'],
        'driver_avg_position': [1.5, 3.2, 4.1, 5.3, 6.8],
        'driver_recent_form': [1.2, 3.5, 4.0, 5.0, 7.2],
        'team_avg_position': [1.5, 3.0, 4.5, 5.0, 1.5],
        'qualifying_position': [1, 3, 2, 5, 4],
        'grid_position': [1, 3, 2, 5, 4],
        'track_experience': [8, 10, 7, 6, 8],
        'points_before_race': [0, 0, 0, 0, 0],
    })
    
    X_pred = model.prepare_features(prediction_data)
    predictions = model.predict(X_pred, model_type='ensemble')
    
    prediction_data['predicted_position'] = predictions.round(0).astype(int)
    prediction_data['confidence'] = np.random.uniform(0.7, 0.95, len(prediction_data))
    
    results = prediction_data[['driver_name', 'qualifying_position', 'predicted_position', 'confidence']]
    results = results.sort_values('predicted_position')
    
    print("\nPredicted Race Results:")
    print(results.to_string(index=False))
    
    # Store predictions in database
    if race_id:
        for _, row in results.iterrows():
            db.insert_prediction(
                race_id=race_id,
                session_type='Race',
                driver_number=int(prediction_data[prediction_data['driver_name'] == row['driver_name']]['driver_number'].values[0]),
                predicted_position=int(row['predicted_position']),
                confidence=float(row['confidence']),
                model_type='ensemble',
                features={'qualifying_position': int(row['qualifying_position'])}
            )
        print(f"\n✓ Stored {len(results)} predictions in database")
    
    # 5. Feature Importance
    print("\n5. FEATURE IMPORTANCE (EXPLAINABILITY)")
    print("-" * 60)
    
    importance = model.get_feature_importance('gradient_boosting')
    print("\nTop features influencing predictions:")
    for i, (feature, value) in enumerate(importance[:5], 1):
        print(f"  {i}. {feature:25s} {value:.4f}")
    
    # Summary
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Run: streamlit run src/streamlit_app.py")
    print("  2. Open: notebooks/f1_ml_pipeline.ipynb")
    print("  3. Explore the database and telemetry data")
    print("\n✓ System ready for use")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
