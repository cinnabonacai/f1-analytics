"""
Formula 1 Race Result Prediction Model
Uses machine learning to predict race outcomes
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report
import joblib
from pathlib import Path


class F1PredictionModel:
    """Predict F1 race results using historical data"""
    
    def __init__(self):
        self.position_model = None
        self.points_model = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, merged_df, qualifying_df=None):
        """Prepare features for prediction"""
        # Create features from historical data
        features_df = merged_df.copy()
        
        # Driver historical stats
        driver_stats = features_df.groupby('driverId').agg({
            'position': ['mean', 'std', 'min'],
            'points': 'mean',
            'wins': lambda x: (x == 1).sum() if 'wins' in features_df.columns else 0
        }).reset_index()
        driver_stats.columns = ['driverId', 'driver_avg_position', 'driver_position_std', 'driver_best_position', 'driver_avg_points', 'driver_wins']
        
        features_df = features_df.merge(driver_stats, on='driverId', how='left')
        
        # Constructor historical stats
        constructor_stats = features_df.groupby('constructorId').agg({
            'position': ['mean', 'std'],
            'points': 'mean'
        }).reset_index()
        constructor_stats.columns = ['constructorId', 'constructor_avg_position', 'constructor_position_std', 'constructor_avg_points']
        
        features_df = features_df.merge(constructor_stats, on='constructorId', how='left')
        
        # Circuit stats
        if 'circuitId' in features_df.columns:
            circuit_stats = features_df.groupby('circuitId').agg({
                'position': 'mean'
            }).reset_index()
            circuit_stats.columns = ['circuitId', 'circuit_avg_position']
            features_df = features_df.merge(circuit_stats, on='circuitId', how='left')
        
        # Year/season features
        features_df['year_normalized'] = (features_df['year'] - features_df['year'].min()) / (features_df['year'].max() - features_df['year'].min())
        
        # Qualifying position (if available)
        if qualifying_df is not None:
            features_df = features_df.merge(
                qualifying_df[['raceId', 'year', 'driverId', 'qualifying_position']],
                on=['raceId', 'year', 'driverId'],
                how='left'
            )
        
        # Grid position
        if 'grid' in features_df.columns:
            features_df['grid_normalized'] = features_df['grid'] / 20.0  # Normalize to 0-1
        
        return features_df
    
    def train_position_model(self, features_df, target_col='position'):
        """Train model to predict final position"""
        # Prepare data
        feature_cols = [
            'driver_avg_position', 'driver_position_std', 'driver_best_position',
            'driver_avg_points', 'driver_wins',
            'constructor_avg_position', 'constructor_position_std', 'constructor_avg_points',
            'year_normalized', 'grid_normalized'
        ]
        
        if 'circuit_avg_position' in features_df.columns:
            feature_cols.append('circuit_avg_position')
        if 'qualifying_position' in features_df.columns:
            feature_cols.append('qualifying_position')
        
        # Filter available features
        available_features = [col for col in feature_cols if col in features_df.columns]
        
        X = features_df[available_features].fillna(0)
        y = features_df[target_col].fillna(20)  # Default to last position if missing
        
        # Remove infinite values
        X = X.replace([np.inf, -np.inf], 0)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.position_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.position_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.position_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"Position Prediction Model - MAE: {mae:.2f}")
        print(f"Feature importance:")
        for feature, importance in zip(available_features, self.position_model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")
        
        return mae
    
    def train_points_model(self, features_df):
        """Train model to predict points"""
        # Prepare data
        feature_cols = [
            'driver_avg_position', 'driver_position_std', 'driver_best_position',
            'driver_avg_points', 'driver_wins',
            'constructor_avg_position', 'constructor_position_std', 'constructor_avg_points',
            'year_normalized', 'grid_normalized'
        ]
        
        if 'circuit_avg_position' in features_df.columns:
            feature_cols.append('circuit_avg_position')
        if 'qualifying_position' in features_df.columns:
            feature_cols.append('qualifying_position')
        
        available_features = [col for col in feature_cols if col in features_df.columns]
        
        X = features_df[available_features].fillna(0)
        y = features_df['points'].fillna(0)
        
        X = X.replace([np.inf, -np.inf], 0)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.points_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.points_model.fit(X_train, y_train)
        
        y_pred = self.points_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"Points Prediction Model - MAE: {mae:.2f}")
        
        return mae
    
    def predict(self, features_df):
        """Predict position and points for given features"""
        if self.position_model is None or self.points_model is None:
            raise ValueError("Models not trained. Call train_position_model and train_points_model first.")
        
        feature_cols = [
            'driver_avg_position', 'driver_position_std', 'driver_best_position',
            'driver_avg_points', 'driver_wins',
            'constructor_avg_position', 'constructor_position_std', 'constructor_avg_points',
            'year_normalized', 'grid_normalized'
        ]
        
        if 'circuit_avg_position' in features_df.columns:
            feature_cols.append('circuit_avg_position')
        if 'qualifying_position' in features_df.columns:
            feature_cols.append('qualifying_position')
        
        available_features = [col for col in feature_cols if col in features_df.columns]
        
        X = features_df[available_features].fillna(0)
        X = X.replace([np.inf, -np.inf], 0)
        
        predicted_position = self.position_model.predict(X)
        predicted_points = self.points_model.predict(X)
        
        return predicted_position, predicted_points
    
    def save_model(self, filepath):
        """Save trained models"""
        joblib.dump({
            'position_model': self.position_model,
            'points_model': self.points_model
        }, filepath)
    
    def load_model(self, filepath):
        """Load trained models"""
        models = joblib.load(filepath)
        self.position_model = models['position_model']
        self.points_model = models['points_model']


if __name__ == "__main__":
    from src.data_cleaner import F1DataCleaner
    
    # Load and prepare data
    data_dir = Path("../data")
    cleaner = F1DataCleaner(data_dir=data_dir)
    cleaner.load_data()
    cleaner.clean_all()
    merged_df = cleaner.merge_data()
    
    # Prepare features
    model = F1PredictionModel()
    features_df = model.prepare_features(merged_df, cleaner.qualifying)
    
    # Train models
    print("Training position prediction model...")
    model.train_position_model(features_df)
    
    print("\nTraining points prediction model...")
    model.train_points_model(features_df)
    
    # Save model
    model.save_model(data_dir / "f1_prediction_model.pkl")
    print("\nModel saved successfully!")

