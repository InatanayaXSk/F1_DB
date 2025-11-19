"""
Machine Learning Models Module
Implements Gradient Boosting and Random Forest models for F1 predictions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os
import json
from datetime import datetime


class F1PredictionModel:
    """Machine learning models for F1 race predictions"""
    
    def __init__(self, model_dir='models'):
        """Initialize prediction model"""
        if not os.path.isabs(model_dir):
            model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), model_dir)
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.gb_model = None
        self.rf_model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.feature_importance = {}
    
    def prepare_features(self, data):
        """
        Prepare features for training/prediction
        Expected columns: driver stats, team stats, circuit characteristics
        """
        feature_columns = [
            'driver_avg_position',
            'driver_recent_form',
            'team_avg_position',
            'grid_position',
            'qualifying_position',
            'track_experience',
            'points_before_race',
        ]
        
        # Select available features
        available_features = [col for col in feature_columns if col in data.columns]
        
        if not available_features:
            raise ValueError("No valid features found in data")
        
        self.feature_names = available_features
        X = data[available_features]
        
        return X
    
    def train_gradient_boosting(self, X_train, y_train, **kwargs):
        """Train Gradient Boosting model"""
        print("\nTraining Gradient Boosting model...")
        
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'learning_rate': kwargs.get('learning_rate', 0.1),
            'max_depth': kwargs.get('max_depth', 5),
            'random_state': kwargs.get('random_state', 42)
        }
        
        self.gb_model = GradientBoostingRegressor(**params)
        self.gb_model.fit(X_train, y_train)
        
        # Calculate feature importance
        self.feature_importance['gradient_boosting'] = dict(
            zip(self.feature_names, self.gb_model.feature_importances_)
        )
        
        print("✓ Gradient Boosting model trained")
        return self.gb_model
    
    def train_random_forest(self, X_train, y_train, **kwargs):
        """Train Random Forest model"""
        print("\nTraining Random Forest model...")
        
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'max_depth': kwargs.get('max_depth', 10),
            'min_samples_split': kwargs.get('min_samples_split', 5),
            'random_state': kwargs.get('random_state', 42)
        }
        
        self.rf_model = RandomForestRegressor(**params)
        self.rf_model.fit(X_train, y_train)
        
        # Calculate feature importance
        self.feature_importance['random_forest'] = dict(
            zip(self.feature_names, self.rf_model.feature_importances_)
        )
        
        print("✓ Random Forest model trained")
        return self.rf_model
    
    def train_ensemble(self, X, y, test_size=0.2):
        """Train both models and create ensemble"""
        print("\n" + "=" * 50)
        print("Training Ensemble Models")
        print("=" * 50)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42
        )
        
        # Train models
        self.train_gradient_boosting(X_train, y_train)
        self.train_random_forest(X_train, y_train)
        
        # Evaluate models
        self.evaluate_models(X_test, y_test)
        
        return self.gb_model, self.rf_model
    
    def evaluate_models(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n" + "=" * 50)
        print("Model Evaluation")
        print("=" * 50)
        
        if self.gb_model:
            gb_pred = self.gb_model.predict(X_test)
            gb_mae = mean_absolute_error(y_test, gb_pred)
            gb_r2 = r2_score(y_test, gb_pred)
            print(f"\nGradient Boosting:")
            print(f"  MAE: {gb_mae:.3f}")
            print(f"  R² Score: {gb_r2:.3f}")
        
        if self.rf_model:
            rf_pred = self.rf_model.predict(X_test)
            rf_mae = mean_absolute_error(y_test, rf_pred)
            rf_r2 = r2_score(y_test, rf_pred)
            print(f"\nRandom Forest:")
            print(f"  MAE: {rf_mae:.3f}")
            print(f"  R² Score: {rf_r2:.3f}")
        
        if self.gb_model and self.rf_model:
            # Ensemble prediction (average)
            ensemble_pred = (gb_pred + rf_pred) / 2
            ensemble_mae = mean_absolute_error(y_test, ensemble_pred)
            ensemble_r2 = r2_score(y_test, ensemble_pred)
            print(f"\nEnsemble (Average):")
            print(f"  MAE: {ensemble_mae:.3f}")
            print(f"  R² Score: {ensemble_r2:.3f}")
    
    def predict(self, X, model_type='ensemble'):
        """Make predictions using specified model"""
        X_scaled = self.scaler.transform(X)
        
        if model_type == 'gradient_boosting' and self.gb_model:
            return self.gb_model.predict(X_scaled)
        elif model_type == 'random_forest' and self.rf_model:
            return self.rf_model.predict(X_scaled)
        elif model_type == 'ensemble' and self.gb_model and self.rf_model:
            gb_pred = self.gb_model.predict(X_scaled)
            rf_pred = self.rf_model.predict(X_scaled)
            return (gb_pred + rf_pred) / 2
        else:
            raise ValueError(f"Model type '{model_type}' not available or not trained")
    
    def get_feature_importance(self, model_type='gradient_boosting'):
        """Get feature importance for explainability"""
        if model_type in self.feature_importance:
            importance = self.feature_importance[model_type]
            sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            return sorted_importance
        return []
    
    def save_models(self, filename_prefix='f1_model'):
        """Save trained models to disk"""
        try:
            # Save Gradient Boosting
            if self.gb_model:
                gb_path = os.path.join(self.model_dir, f"{filename_prefix}_gb.pkl")
                with open(gb_path, 'wb') as f:
                    pickle.dump(self.gb_model, f)
                print(f"✓ Saved Gradient Boosting model: {gb_path}")
            
            # Save Random Forest
            if self.rf_model:
                rf_path = os.path.join(self.model_dir, f"{filename_prefix}_rf.pkl")
                with open(rf_path, 'wb') as f:
                    pickle.dump(self.rf_model, f)
                print(f"✓ Saved Random Forest model: {rf_path}")
            
            # Save scaler
            scaler_path = os.path.join(self.model_dir, f"{filename_prefix}_scaler.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Save metadata
            metadata = {
                'feature_names': self.feature_names,
                'feature_importance': self.feature_importance,
                'saved_at': datetime.now().isoformat()
            }
            meta_path = os.path.join(self.model_dir, f"{filename_prefix}_metadata.json")
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("✓ All models saved successfully")
        
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def load_models(self, filename_prefix='f1_model'):
        """Load trained models from disk"""
        try:
            # Load Gradient Boosting
            gb_path = os.path.join(self.model_dir, f"{filename_prefix}_gb.pkl")
            if os.path.exists(gb_path):
                with open(gb_path, 'rb') as f:
                    self.gb_model = pickle.load(f)
                print(f"✓ Loaded Gradient Boosting model")
            
            # Load Random Forest
            rf_path = os.path.join(self.model_dir, f"{filename_prefix}_rf.pkl")
            if os.path.exists(rf_path):
                with open(rf_path, 'rb') as f:
                    self.rf_model = pickle.load(f)
                print(f"✓ Loaded Random Forest model")
            
            # Load scaler
            scaler_path = os.path.join(self.model_dir, f"{filename_prefix}_scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            # Load metadata
            meta_path = os.path.join(self.model_dir, f"{filename_prefix}_metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get('feature_names', [])
                    self.feature_importance = metadata.get('feature_importance', {})
            
            print("✓ All models loaded successfully")
            return True
        
        except Exception as e:
            print(f"Error loading models: {e}")
            return False


def create_sample_data():
    """Create sample training data for demonstration"""
    np.random.seed(42)
    n_samples = 500
    
    data = pd.DataFrame({
        'driver_avg_position': np.random.uniform(1, 20, n_samples),
        'driver_recent_form': np.random.uniform(1, 20, n_samples),
        'team_avg_position': np.random.uniform(1, 10, n_samples),
        'grid_position': np.random.randint(1, 21, n_samples),
        'qualifying_position': np.random.randint(1, 21, n_samples),
        'track_experience': np.random.randint(0, 10, n_samples),
        'points_before_race': np.random.uniform(0, 400, n_samples),
    })
    
    # Simulate race position as target (correlated with features)
    data['race_position'] = (
        0.3 * data['qualifying_position'] +
        0.2 * data['driver_avg_position'] +
        0.2 * data['team_avg_position'] +
        np.random.normal(0, 2, n_samples)
    ).clip(1, 20)
    
    return data


def main():
    """Main function to demonstrate ML models"""
    print("\nF1 Prediction Models")
    print("=" * 50)
    
    # Create sample data
    print("\nGenerating sample training data...")
    data = create_sample_data()
    print(f"✓ Created {len(data)} training samples")
    
    # Initialize model
    model = F1PredictionModel()
    
    # Prepare features
    X = model.prepare_features(data)
    y = data['race_position']
    
    print(f"\nFeatures: {model.feature_names}")
    
    # Train ensemble
    model.train_ensemble(X, y)
    
    # Show feature importance
    print("\n" + "=" * 50)
    print("Feature Importance (Gradient Boosting)")
    print("=" * 50)
    for feature, importance in model.get_feature_importance('gradient_boosting'):
        print(f"  {feature}: {importance:.4f}")
    
    # Save models
    model.save_models('f1_race_model')
    
    # Test loading
    print("\nTesting model loading...")
    test_model = F1PredictionModel()
    test_model.load_models('f1_race_model')
    
    print("\n✓ ML models demonstration complete!")


if __name__ == "__main__":
    main()
