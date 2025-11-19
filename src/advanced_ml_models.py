"""
Advanced ML Models Module
Implements ranking models, stacked ensemble, probabilistic predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
from scipy.stats import spearmanr
from scipy.special import softmax
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
import shap
import joblib
import os
import json
from datetime import datetime


class AdvancedF1Predictor:
    """Advanced ML models for F1 predictions with ranking objectives"""
    
    def __init__(self, model_dir='models'):
        """Initialize advanced predictor"""
        if not os.path.isabs(model_dir):
            model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), model_dir)
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Base models
        self.lgb_model = None
        self.xgb_model = None
        self.catboost_model = None
        self.rf_model = None
        self.gb_model = None
        self.ridge_model = None
        
        # Meta model for stacking
        self.meta_model = None
        
        # Feature scaling
        self.scaler = StandardScaler()
        self.feature_names = []
        
        # SHAP explainer
        self.explainer = None
        
        # Training history
        self.training_history = []
    
    def prepare_ranking_data(self, X, y, race_groups):
        """
        Prepare data for ranking objectives
        
        Args:
            X: Feature matrix
            y: Target positions
            race_groups: Array indicating which race each sample belongs to
        
        Returns:
            X, y, group_data for ranking models
        """
        # Sort by race and position
        sort_idx = np.lexsort((y, race_groups))
        X_sorted = X[sort_idx]
        y_sorted = y[sort_idx]
        groups_sorted = race_groups[sort_idx]
        
        # Calculate group sizes (number of drivers per race)
        unique_groups, group_counts = np.unique(groups_sorted, return_counts=True)
        
        return X_sorted, y_sorted, group_counts
    
    def train_lightgbm_ranker(self, X_train, y_train, race_groups_train, 
                              X_val=None, y_val=None, race_groups_val=None):
        """Train LightGBM with lambdarank objective"""
        print("\nTraining LightGBM Ranker...")
        
        # Prepare ranking data
        X_sorted, y_sorted, groups = self.prepare_ranking_data(
            X_train, y_train, race_groups_train
        )
        
        # Create dataset
        train_data = lgb.Dataset(X_sorted, label=y_sorted, group=groups)
        
        params = {
            'objective': 'lambdarank',
            'metric': 'ndcg',
            'ndcg_eval_at': [1, 3, 5, 10],
            'learning_rate': 0.05,
            'num_leaves': 31,
            'max_depth': 8,
            'min_data_in_leaf': 20,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': 42
        }
        
        # Validation data if provided
        valid_sets = [train_data]
        if X_val is not None:
            X_val_sorted, y_val_sorted, groups_val = self.prepare_ranking_data(
                X_val, y_val, race_groups_val
            )
            val_data = lgb.Dataset(X_val_sorted, label=y_val_sorted, group=groups_val)
            valid_sets.append(val_data)
        
        # Train
        self.lgb_model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            valid_sets=valid_sets,
            callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
        )
        
        print("✓ LightGBM Ranker trained")
        return self.lgb_model
    
    def train_xgboost_ranker(self, X_train, y_train, race_groups_train):
        """Train XGBoost with rank:pairwise objective"""
        print("\nTraining XGBoost Ranker...")
        
        X_sorted, y_sorted, groups = self.prepare_ranking_data(
            X_train, y_train, race_groups_train
        )
        
        # Create group boundaries
        group_boundaries = np.cumsum(groups)
        
        params = {
            'objective': 'rank:pairwise',
            'eval_metric': 'ndcg',
            'learning_rate': 0.05,
            'max_depth': 8,
            'min_child_weight': 5,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'tree_method': 'hist'
        }
        
        dtrain = xgb.DMatrix(X_sorted, label=y_sorted)
        dtrain.set_group(groups)
        
        self.xgb_model = xgb.train(
            params,
            dtrain,
            num_boost_round=500,
            verbose_eval=False
        )
        
        print("✓ XGBoost Ranker trained")
        return self.xgb_model
    
    def train_base_models(self, X_train, y_train):
        """Train base models for stacking"""
        print("\nTraining base models...")
        
        # CatBoost
        print("  Training CatBoost...")
        self.catboost_model = CatBoostRegressor(
            iterations=500,
            learning_rate=0.05,
            depth=8,
            loss_function='MAE',
            random_state=42,
            verbose=False
        )
        self.catboost_model.fit(X_train, y_train)
        
        # Random Forest
        print("  Training Random Forest...")
        self.rf_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        
        # Gradient Boosting
        print("  Training Gradient Boosting...")
        self.gb_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=8,
            random_state=42
        )
        self.gb_model.fit(X_train, y_train)
        
        # Ridge Regression
        print("  Training Ridge Regression...")
        self.ridge_model = Ridge(alpha=1.0, random_state=42)
        self.ridge_model.fit(X_train, y_train)
        
        print("✓ Base models trained")
    
    def create_stacked_predictions(self, X):
        """Create meta-features from base model predictions"""
        meta_features = []
        
        if self.catboost_model:
            meta_features.append(self.catboost_model.predict(X).reshape(-1, 1))
        if self.rf_model:
            meta_features.append(self.rf_model.predict(X).reshape(-1, 1))
        if self.gb_model:
            meta_features.append(self.gb_model.predict(X).reshape(-1, 1))
        if self.ridge_model:
            meta_features.append(self.ridge_model.predict(X).reshape(-1, 1))
        
        if len(meta_features) == 0:
            raise ValueError("No base models trained")
        
        return np.hstack(meta_features)
    
    def train_meta_model(self, X_train, y_train, race_groups_train):
        """Train meta-model on base model predictions"""
        print("\nTraining meta-model (LightGBM)...")
        
        # Get base model predictions
        meta_X_train = self.create_stacked_predictions(X_train)
        
        # Train meta model with ranking
        X_sorted, y_sorted, groups = self.prepare_ranking_data(
            meta_X_train, y_train, race_groups_train
        )
        
        train_data = lgb.Dataset(X_sorted, label=y_sorted, group=groups)
        
        params = {
            'objective': 'lambdarank',
            'metric': 'ndcg',
            'learning_rate': 0.05,
            'num_leaves': 15,
            'max_depth': 5,
            'verbose': -1,
            'random_state': 42
        }
        
        self.meta_model = lgb.train(
            params,
            train_data,
            num_boost_round=200
        )
        
        print("✓ Meta-model trained")
        return self.meta_model
    
    def train_ensemble(self, X, y, race_groups, test_size=0.2):
        """Train full stacked ensemble"""
        print("\n" + "=" * 50)
        print("Training Stacked Ensemble")
        print("=" * 50)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Time-based split
        split_idx = int(len(X_scaled) * (1 - test_size))
        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        race_groups_train = race_groups[:split_idx]
        race_groups_test = race_groups[split_idx:]
        
        # Train base models
        self.train_base_models(X_train, y_train)
        
        # Train ranking models
        self.train_lightgbm_ranker(X_train, y_train, race_groups_train)
        self.train_xgboost_ranker(X_train, y_train, race_groups_train)
        
        # Train meta model
        self.train_meta_model(X_train, y_train, race_groups_train)
        
        # Evaluate
        self.evaluate_models(X_test, y_test, race_groups_test)
        
        # Initialize SHAP explainer
        print("\nInitializing SHAP explainer...")
        self.explainer = shap.TreeExplainer(self.lgb_model)
        print("✓ SHAP explainer ready")
        
        return self.lgb_model, self.meta_model
    
    def time_series_cv(self, X, y, race_groups, n_splits=5):
        """Time-aware cross-validation with rolling window"""
        print("\n" + "=" * 50)
        print(f"Time Series Cross-Validation ({n_splits} splits)")
        print("=" * 50)
        
        X_scaled = self.scaler.fit_transform(X)
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_scores = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X_scaled)):
            print(f"\nFold {fold + 1}/{n_splits}")
            
            X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            groups_train = race_groups[train_idx]
            groups_val = race_groups[val_idx]
            
            # Train on this fold
            self.train_base_models(X_train, y_train)
            self.train_lightgbm_ranker(X_train, y_train, groups_train, 
                                      X_val, y_val, groups_val)
            
            # Evaluate
            scores = self.evaluate_models(X_val, y_val, groups_val, verbose=False)
            cv_scores.append(scores)
            
            print(f"  MAE: {scores['mae']:.3f}, Spearman: {scores['spearman']:.3f}")
        
        # Average scores
        avg_scores = {
            'mae': np.mean([s['mae'] for s in cv_scores]),
            'spearman': np.mean([s['spearman'] for s in cv_scores]),
            'top10_acc': np.mean([s['top10_acc'] for s in cv_scores])
        }
        
        print("\n" + "=" * 50)
        print("Cross-Validation Results")
        print("=" * 50)
        print(f"Average MAE: {avg_scores['mae']:.3f}")
        print(f"Average Spearman: {avg_scores['spearman']:.3f}")
        print(f"Average Top-10 Accuracy: {avg_scores['top10_acc']:.3f}")
        
        return cv_scores, avg_scores
    
    def evaluate_models(self, X_test, y_test, race_groups_test, verbose=True):
        """Evaluate model performance with multiple metrics"""
        if verbose:
            print("\n" + "=" * 50)
            print("Model Evaluation")
            print("=" * 50)
        
        scores = {}
        
        # LightGBM predictions
        if self.lgb_model:
            lgb_pred = self.lgb_model.predict(X_test)
            
            # Mean Absolute Position Error
            mae = mean_absolute_error(y_test, lgb_pred)
            scores['mae'] = mae
            
            # Spearman correlation
            spearman, _ = spearmanr(y_test, lgb_pred)
            scores['spearman'] = spearman
            
            # Top-10 accuracy (per race)
            top10_acc = self.calculate_top10_accuracy(y_test, lgb_pred, race_groups_test)
            scores['top10_acc'] = top10_acc
            
            if verbose:
                print(f"\nLightGBM Ranker:")
                print(f"  Mean Absolute Position Error: {mae:.3f}")
                print(f"  Spearman Correlation: {spearman:.3f}")
                print(f"  Top-10 Accuracy: {top10_acc:.3f}")
        
        # Ensemble predictions
        if self.meta_model and all([self.catboost_model, self.rf_model, 
                                    self.gb_model, self.ridge_model]):
            meta_X = self.create_stacked_predictions(X_test)
            ensemble_pred = self.meta_model.predict(meta_X)
            
            ensemble_mae = mean_absolute_error(y_test, ensemble_pred)
            ensemble_spearman, _ = spearmanr(y_test, ensemble_pred)
            ensemble_top10 = self.calculate_top10_accuracy(y_test, ensemble_pred, race_groups_test)
            
            scores['ensemble_mae'] = ensemble_mae
            scores['ensemble_spearman'] = ensemble_spearman
            scores['ensemble_top10'] = ensemble_top10
            
            if verbose:
                print(f"\nStacked Ensemble:")
                print(f"  Mean Absolute Position Error: {ensemble_mae:.3f}")
                print(f"  Spearman Correlation: {ensemble_spearman:.3f}")
                print(f"  Top-10 Accuracy: {ensemble_top10:.3f}")
        
        return scores
    
    def calculate_top10_accuracy(self, y_true, y_pred, race_groups):
        """Calculate accuracy of predicting top-10 finishers"""
        unique_races = np.unique(race_groups)
        correct_predictions = 0
        total_predictions = 0
        
        for race in unique_races:
            race_mask = race_groups == race
            true_positions = y_true[race_mask]
            pred_positions = y_pred[race_mask]
            
            # Get indices of true and predicted top-10
            true_top10 = set(np.where(true_positions <= 10)[0])
            pred_top10 = set(np.argsort(pred_positions)[:10])
            
            # Count correct predictions
            correct = len(true_top10.intersection(pred_top10))
            correct_predictions += correct
            total_predictions += 10
        
        return correct_predictions / total_predictions if total_predictions > 0 else 0
    
    def predict_with_probabilities(self, X, n_positions=20):
        """
        Predict positions with probability distribution
        
        Args:
            X: Feature matrix
            n_positions: Number of possible positions
        
        Returns:
            positions: Predicted positions
            probabilities: Probability matrix (n_samples x n_positions)
        """
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from LightGBM
        predictions = self.lgb_model.predict(X_scaled)
        
        # Convert to probabilities using softmax
        # Lower predicted position = higher probability of that position
        probabilities = np.zeros((len(predictions), n_positions))
        
        for i, pred in enumerate(predictions):
            # Create distribution centered around prediction
            scores = -np.abs(np.arange(1, n_positions + 1) - pred)
            probs = softmax(scores)
            probabilities[i] = probs
        
        return predictions, probabilities
    
    def get_shap_values(self, X, driver_indices=None):
        """
        Calculate SHAP values for explainability
        
        Args:
            X: Feature matrix
            driver_indices: Specific drivers to explain (None = all)
        
        Returns:
            shap_values: SHAP value matrix
        """
        if self.explainer is None:
            print("SHAP explainer not initialized. Training required.")
            return None
        
        X_scaled = self.scaler.transform(X)
        
        if driver_indices is not None:
            X_scaled = X_scaled[driver_indices]
        
        shap_values = self.explainer.shap_values(X_scaled)
        
        return shap_values
    
    def get_feature_importance(self, top_n=10):
        """Get top N most important features"""
        if self.lgb_model is None:
            return []
        
        importance = self.lgb_model.feature_importance(importance_type='gain')
        feature_importance = list(zip(self.feature_names, importance))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return feature_importance[:top_n]
    
    def save_models(self, prefix='advanced_f1'):
        """Save all trained models"""
        print(f"\nSaving models to {self.model_dir}...")
        
        # Save LightGBM
        if self.lgb_model:
            lgb_path = os.path.join(self.model_dir, f"{prefix}_lgb.txt")
            self.lgb_model.save_model(lgb_path)
            print(f"✓ Saved LightGBM: {lgb_path}")
        
        # Save XGBoost
        if self.xgb_model:
            xgb_path = os.path.join(self.model_dir, f"{prefix}_xgb.json")
            self.xgb_model.save_model(xgb_path)
            print(f"✓ Saved XGBoost: {xgb_path}")
        
        # Save other models with joblib
        models_to_save = {
            'catboost': self.catboost_model,
            'rf': self.rf_model,
            'gb': self.gb_model,
            'ridge': self.ridge_model,
            'meta': self.meta_model,
            'scaler': self.scaler
        }
        
        for name, model in models_to_save.items():
            if model is not None:
                path = os.path.join(self.model_dir, f"{prefix}_{name}.pkl")
                joblib.dump(model, path)
                print(f"✓ Saved {name}: {path}")
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'training_history': self.training_history,
            'saved_at': datetime.now().isoformat()
        }
        meta_path = os.path.join(self.model_dir, f"{prefix}_metadata.json")
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ All models saved successfully")
    
    def load_models(self, prefix='advanced_f1'):
        """Load all trained models"""
        print(f"\nLoading models from {self.model_dir}...")
        
        try:
            # Load LightGBM
            lgb_path = os.path.join(self.model_dir, f"{prefix}_lgb.txt")
            if os.path.exists(lgb_path):
                self.lgb_model = lgb.Booster(model_file=lgb_path)
                print(f"✓ Loaded LightGBM")
            
            # Load XGBoost
            xgb_path = os.path.join(self.model_dir, f"{prefix}_xgb.json")
            if os.path.exists(xgb_path):
                self.xgb_model = xgb.Booster()
                self.xgb_model.load_model(xgb_path)
                print(f"✓ Loaded XGBoost")
            
            # Load other models
            model_names = ['catboost', 'rf', 'gb', 'ridge', 'meta', 'scaler']
            for name in model_names:
                path = os.path.join(self.model_dir, f"{prefix}_{name}.pkl")
                if os.path.exists(path):
                    model = joblib.load(path)
                    setattr(self, f"{name}_model" if name != 'scaler' else 'scaler', model)
                    print(f"✓ Loaded {name}")
            
            # Load metadata
            meta_path = os.path.join(self.model_dir, f"{prefix}_metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_names = metadata.get('feature_names', [])
                    self.training_history = metadata.get('training_history', [])
            
            # Initialize SHAP
            if self.lgb_model:
                self.explainer = shap.TreeExplainer(self.lgb_model)
                print("✓ SHAP explainer initialized")
            
            print("✓ All models loaded successfully")
            return True
        
        except Exception as e:
            print(f"Error loading models: {e}")
            return False


def main():
    """Demonstration of advanced ML models"""
    print("\nAdvanced F1 Prediction Models")
    print("=" * 50)
    
    # Create sample data
    np.random.seed(42)
    n_races = 10
    n_drivers = 20
    n_samples = n_races * n_drivers
    
    # Features
    X = np.random.randn(n_samples, 15)
    
    # Target: positions (1-20)
    y = np.tile(np.arange(1, n_drivers + 1), n_races) + np.random.randn(n_samples) * 2
    y = np.clip(y, 1, 20)
    
    # Race groups
    race_groups = np.repeat(np.arange(n_races), n_drivers)
    
    # Initialize model
    predictor = AdvancedF1Predictor()
    predictor.feature_names = [f'feature_{i}' for i in range(15)]
    
    # Train
    print("\nTraining models...")
    predictor.train_ensemble(X, y, race_groups, test_size=0.2)
    
    # Make predictions
    print("\nMaking predictions...")
    X_test = X[-40:]
    predictions, probabilities = predictor.predict_with_probabilities(X_test, n_positions=20)
    
    print(f"Predicted positions: {predictions[:5]}")
    print(f"Top-3 probabilities shape: {probabilities[:5, :3].shape}")
    
    # Feature importance
    print("\nTop 5 Features:")
    for feature, importance in predictor.get_feature_importance(top_n=5):
        print(f"  {feature}: {importance:.2f}")
    
    # Save models
    predictor.save_models('demo_model')
    
    print("\n✓ Advanced ML demonstration complete!")


if __name__ == "__main__":
    main()
